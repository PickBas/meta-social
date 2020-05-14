from django.shortcuts import render


class PostViews:
    """
    PostViews
    """

    class PostView(View):
        """
        PostView
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/full_post.html'

        def get(self, request, **kwargs) -> render:
            """
            Processing get request
            """
            context = get_menu_context('post', 'Пост')
            context['post'] = Post.objects.get(id=kwargs['post_id'])

            return render(request, self.template_name, context)

    class PostUrLikes(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'profile/like_marks.html'
            self.context = get_menu_context('like_marks', 'Закладки')

        def get(self, request) -> render:
            """
            Processing get request
            """
            return render(request, self.template_name, self.context)

    class PostEdit(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/post_edit.html'
            self.context = get_menu_context('post', 'Редактирование поста')

        def post(self, request, **kwargs):
            """
            Process post request. Changing position, deleting, changing text, changing images of post
            """
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            PostImageFormSet = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )

            postform = PostForm(request.POST)
            formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImages.objects.none())

            if request.method == 'POST':
                if postform.is_valid() and formset.is_valid():
                    postform.save()
                    
                    for form in formset.ordered_forms:
                        print(form.cleaned_data)
                        if form.cleaned_data['image'] is None:
                            form.cleaned_data['id'].order = form.cleaned_data['ORDER']
                            form.cleaned_data['id'].save()
                        elif form.cleaned_data['image'] == False:
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
                    
            self.context['postform'] = PostForm(instance=post_item)
            initial_images = [{'image': i.image} for i in post_item.get_images() if i.image]
            self.context['formset'] = PostImageFormSet(initial=initial_images, queryset=post_item.get_images())

            return render(request, self.template_name, self.context)

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            PostImageFormSet = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )
            
            self.context['postform'] = PostForm(instance=post_item)
            initial_images = [{'image': i.image} for i in post_item.get_images() if i.image]
            self.context['formset'] = PostImageFormSet(initial=initial_images, queryset=post_item.get_images())
            
            return render(request, self.template_name, self.context)

    class PostAjax(View):
        @staticmethod
        def post(request, **kwargs):
            """
            Send comment to post from full post page
            """
            if request.method == "POST":
                if len(request.POST.get('text')) > 0:
                    comment_item = Comment(
                        text=request.POST.get('text'),
                        post=Post.objects.get(id=kwargs['post_id']),
                        user=request.user
                    )
                    comment_item.save()

                    json_response = json.dumps({'id': comment_item.user.id,
                                                'username': comment_item.user.username,
                                                'text': comment_item.text,
                                                'date': str(comment_item.date)})

                    return HttpResponse(json_response, content_type="application/json")
                raise Http404()


    @staticmethod
    def send_comment(request, post_id):
        """
        Send comment to post from feed
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
        :param request: request
        :return: HttpResponseRedirect
        """
        PostImageFormSet = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10)

        if request.method == "POST":
            postForm = PostForm(request.POST)
            formset = PostImageFormSet(
                request.POST, request.FILES, queryset=PostImages.objects.none()
            )

            if postForm.is_valid() and formset.is_valid():
                post_form = postForm.save(commit=False)
                post_form.user = request.user
                post_form.save()

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImages(post=post_form, image=image, from_user_id=request.user.id)
                        photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def post_remove(request, post_id) -> HttpResponseRedirect:
        """
        Removing a post using Ajax
        :param request: request
        :param post_id: id of a post want to be deleted
        :return: HttpResponseRedirect
        """
        if request.method == "POST":
            Post.objects.get(id=post_id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    @staticmethod
    def like_post(request, post_id):
        """
        Method for like or unlike post
        """
        if request.method == 'POST':
            post_item = get_object_or_404(Post, id=post_id)

            if post_item in request.user.profile.liked_posts.all():
                request.user.profile.liked_posts.remove(post_item)
                post_item.likes.all().filter(user=request.user).delete()

                return HttpResponse('unliked')
            else:
                post_item.likes.create(user=request.user)
                request.user.profile.liked_posts.add(post_item)

                return HttpResponse('liked')

        raise Http404()