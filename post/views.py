"""
Meta social post views
"""
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.forms import modelformset_factory

from index.views import MetaSocialView
from music.models import Music

from .models import Post, PostImages, Comment
from .forms import EditPostImageForm, PostImageForm, PostForm


class PostViews:
    """
    PostViews
    """

    class PostView(MetaSocialView):
        """
        PostView
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/full_post.html'

        def get(self, request, **kwargs) -> render:
            """
            Representation of post
        
            :param post_id: post id
            :type post_id: int
            :param request: object with request details
            :type request: :class:`django.http.HttpRequest`
            :return: responce object with HTML code
            :rtype: :class:`django.http.HttpResponse`
            :raises: :class:`django.http.Http404` if post_id not valid
            """
            context = self.get_menu_context('post', 'Пост')
            context['post'] = get_object_or_404(Post, id=kwargs['post_id'])
            context['all'] = True

            return render(request, self.template_name, context)

    class PostUrLikes(MetaSocialView):
        """
        User liked posts representation
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'profile/like_marks.html'
            self.context = self.get_menu_context('like_marks', 'Закладки')

        def get(self, request) -> render:
            """
            Representation of liked posts
        
            :param request: object with request details
            :type request: :class:`django.http.HttpRequest`
            :return: responce object with HTML code
            :rtype: :class:`django.http.HttpResponse`
            """
            return render(request, self.template_name, self.context)

    class PostEdit(MetaSocialView):
        """
        Post editing representaion and functionality
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/post_edit.html'
            self.context = self.get_menu_context('post', 'Редактирование поста')

        def post(self, request, **kwargs):
            """
            Process post request.
            
            Changing position, deleting, changing text, changing images of post
        
            :param post_id: post id
            :type post_id: int
            :param request: object with request details
            :type request: :class:`django.http.HttpRequest`
            :return: responce object with HTML code
            :rtype: :class:`django.http.HttpResponse`
            :raises: :class:`django.http.Http404` if post_id not valid
            """
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            post_image_form_set = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )

            postform = PostForm(request.POST)
            formset = post_image_form_set(request.POST, request.FILES,
                                          queryset=PostImages.objects.none())

            if request.method == 'POST':
                if postform.is_valid() and formset.is_valid():
                    post_item.text = postform.cleaned_data['text']
                    post_item.save()

                    for form in formset.ordered_forms:
                        if form.cleaned_data['image'] is None:
                            form.cleaned_data['id'].order = form.cleaned_data['ORDER']
                            form.cleaned_data['id'].save()
                        elif not form.cleaned_data['image']:
                            if form.cleaned_data['id']:
                                form.cleaned_data['id'].delete()
                        else:
                            if form.cleaned_data['id']:
                                form.cleaned_data['id'].image = form.cleaned_data['image']
                                form.cleaned_data['id'].save()
                            else:
                                item = PostImages(
                                    post=post_item,
                                    order=form.cleaned_data['ORDER'],
                                    image=form.cleaned_data['image']
                                )
                                item.save()

            return redirect(post_item.get_link())

        def get(self, request, **kwargs):
            """
            Representation of post
        
            :param post_id: post id
            :type post_id: int
            :param request: object with request details
            :type request: :class:`django.http.HttpRequest`
            :return: responce object with HTML code
            :rtype: :class:`django.http.HttpResponse`
            :raises: :class:`django.http.Http404` if post_id not valid
            """
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            post_image_form_set = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )

            self.context['postform'] = PostForm(instance=post_item)
            initial_images = [{'image': i.image} for i in post_item.get_images() if i.image]
            self.context['formset'] = post_image_form_set(initial=initial_images,
                                                          queryset=post_item.get_images())
            self.context['images_less_ten'] = post_item.get_images().count() < 10

            return render(request, self.template_name, self.context)

    @staticmethod
    def send_comment(request, post_id):
        """
        Send comment to post from feed
    
        :param post_id: post id
        :type post_id: int
        :param request: object with request details
        :type request: :class:`django.http.HttpRequest`
        :return: responce object with HTML code
        :rtype: :class:`django.http.HttpResponse`
        :raises: :class:`django.http.Http404` if post_id not valid
        """
        if request.method == 'POST' and request.POST.get('text'):
            post_item = get_object_or_404(Post, id=post_id)

            comment_item = Comment(
                text=request.POST.get('text'),
                post=post_item,
                user=request.user
            )
            comment_item.save()

            return render(request, 'post/post.html', {'post': post_item})

        raise Http404()

    @staticmethod
    def post_new(request):
        """
        Function for creating post
    
        :param request: object with request details
        :type request: :class:`django.http.HttpRequest`
        :return: responce redirect
        :rtype: :class:`django.http.HttpResponseRedirect`
        """
        post_image_form_set = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10)

        if request.method == "POST":
            post_form = PostForm(request.POST)
            formset = post_image_form_set(
                request.POST, request.FILES, queryset=PostImages.objects.none()
            )

            if post_form.is_valid() and formset.is_valid():
                post_form = post_form.save(commit=False)
                post_form.user = post_form.owner = request.user
                post_form.save()

                if request.POST.get('music'):
                    for music_id in [int(i) for i in request.POST.get('music').split()]:
                        music_item = get_object_or_404(Music, id=music_id)
                        post_form.music.add(music_item)

                request.user.profile.posts.add(post_form)

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImages(post=post_form, image=image,
                                           from_user_id=request.user.id)
                        photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def post_remove(request, post_id) -> HttpResponseRedirect:
        """
        Removing a post using Ajax
    
        :param post_id: post id
        :type post_id: int
        :param request: object with request details
        :type request: :class:`django.http.HttpRequest`
        :return: responce object with HTML code
        :rtype: :class:`django.http.HttpResponse`
        :raises: :class:`django.http.Http404` if post_id not valid
        """
        if request.method == "POST":
            get_object_or_404(Post, id=post_id).delete()
        return HttpResponse('Success')

    @staticmethod
    def like_post(request, post_id):
        """
        Method for like or unlike post
    
        :param post_id: post id
        :type post_id: int
        :param request: object with request details
        :type request: :class:`django.http.HttpRequest`
        :return: responce object with HTML code
        :rtype: :class:`django.http.HttpResponse`
        :raises: :class:`django.http.Http404` if post_id not valid
        """
        if request.method == 'POST':
            post_item = get_object_or_404(Post, id=post_id)

            if post_item in request.user.profile.liked_posts.all():
                request.user.profile.liked_posts.remove(post_item)
                post_item.likes.all().filter(user=request.user).delete()

                return HttpResponse('unliked')

            post_item.likes.create(user=request.user)
            request.user.profile.liked_posts.add(post_item)

            return HttpResponse('liked')

        raise Http404()

    @staticmethod
    def get_comments(request, post_id, is_all):
        """
        Returns rendered response of post comments
    
        :param post_id: post id
        :type post_id: int
        :param is_all: return count
        :type is_all: int
        :param request: object with request details
        :type request: :class:`django.http.HttpRequest`
        :return: responce object with HTML code
        :rtype: :class:`django.http.HttpResponse`
        :raises: :class:`django.http.Http404` if post_id not valid
        """
        if request.method == 'POST' and is_all in [0, 1]:
            post_item = get_object_or_404(Post, id=post_id)

            return render(request, 'post/comments.html', {'post': post_item, 'all': bool(is_all)})

        raise Http404()

    @staticmethod
    def rt(request, post_id):
        """
        Function for rt
        :param post_id: post
        :param request: request
        :return: HttpResponseRedirect
        """

        post = Post.objects.get(id=post_id)
        new_post = Post.objects.create(user=request.user, text=post.text, is_reposted=True)

        if post.owner:
            new_post.owner = post.owner
        elif post.owner_community:
            new_post.owner_community = post.owner_community

        post.rt.add(request.user)
        new_post.save()
        request.user.profile.posts.add(new_post)

        if post.get_images():
            for img in post.get_images():
                photo = PostImages(post=new_post, image=img.image, from_user_id=request.user.id)
            photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
