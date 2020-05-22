"""
Meta social friends views
"""

from simple_search import search_filter

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import Http404

from core.views import MetaSocialView

from .models import FriendshipRequest
from user_profile.models import Profile


class FriendsViews:
    """
    Class containing friends functionality and representation
    """
    @staticmethod
    def get_render(request, context):
        """
        Friends search. Returns rendered responce
        """
        context['matching'] = True
        if not request.POST.get('query'):
            context['matching'] = False
            context['friendlist'] = context['c_user'].profile.friends.all()
            return render(request, 'friends/list.html', context)

        query = request.POST.get('query')
        search_fields = ['username', 'first_name', 'last_name']

        context['f_matches'] = User.objects.filter(search_filter(search_fields, query)).exclude(id=request.user.id)

        return render(request, 'friends/list.html', context)

    class FriendsList(MetaSocialView):
        """
        Friends list view
        """
        def __init__(self, **kwargs):
            self.template_name = 'friends/friends_list.html'
            self.context = self.get_menu_context('friends', 'Список друзей')
            super().__init__(**kwargs)

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            requested = request.GET.get('username')
            self.context['c_user'] = request.user
            if requested:
                self.context['c_user'] = User.objects.get(profile=Profile.objects.get(custom_url=requested))
            self.context['friends_pages'] = 'my_list'

            self.pagination_elemetns(
                request,
                self.context['c_user'].profile.friends.all(),
                self.context,
                'friendlist'
            )

            return render(request, self.template_name, self.context)

        def post(self, request, **kwargs):
            """
            Processing post request
            """
            self.context['c_user'] = request.user
            return FriendsViews.get_render(request, self.context)

    class FriendsRequests(MetaSocialView):
        """
        Requests view
        """
        def __init__(self, **kwargs):
            self.template_name = 'friends/requests.html'
            super().__init__(**kwargs)

        def get(self, request):
            """
            Processing get request
            """
            context = self.get_menu_context('friends', 'Заявки в друзья')

            context['c_user'] = request.user
            context['friends_pages'] = 'requests'
            context['friendship'] = {
                'incoming': request.user.profile.friendship_inbox_requests(),
                'outcoming': request.user.profile.friendship_outbox_requests(),
            }

            return render(request, self.template_name, context)

    class FriendsBlacklist(MetaSocialView):
        """
        Blacklist view
        """
        def __init__(self, **kwargs):
            self.template_name = 'friends/blacklist.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs) -> render:
            """
            Friends_blacklist view
            :param user_id: user in blacklist od
            :param request: request
            :return: render
            """
            context = self.get_menu_context('friends', 'Черный список')

            c_user = request.user
            context['c_user'] = c_user
            context['friends_pages'] = 'blacklist'

            return render(request, self.template_name, context)

    class SendFriendshipRequest(MetaSocialView):
        """
        Class for sending friendship request
        """
        def __init__(self, **kwargs):
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs) -> redirect:
            """
            Sending friendship request view
            :param request: request
            :param user_id: id
            :return: redirect
            """

            self.user_item = get_object_or_404(User, id=kwargs['user_id'])

            if not FriendshipRequest.objects.filter(from_user=self.user_item, to_user=request.user).exists():
                if not FriendshipRequest.objects.filter(from_user=request.user, to_user=self.user_item).exists():
                    item = FriendshipRequest(
                        from_user=request.user,
                        to_user=self.user_item,
                    )

                    item.save()

                    return FriendsViews.get_render(request, {'c_user': request.user})

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            raise Http404()

    class AcceptRequest(MetaSocialView):
        """
        Class for accepting friendship request
        """
        def __init__(self, **kwargs):
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs) -> redirect:
            """
            Accept_request view
            :param request: request
            :param request_id: id
            :return: redirect
            """
            if request.method == 'POST':
                user_item = get_object_or_404(User, id=kwargs['user_id'])

                if FriendshipRequest.objects.filter(from_user=user_item, to_user=request.user).exists():
                    request_item = FriendshipRequest.objects.get(
                        from_user=user_item, to_user=request.user)
                elif FriendshipRequest.objects.filter(from_user=request.user, to_user=user_item).exists():
                    request_item = FriendshipRequest.objects.get(
                        from_user=request.user, to_user=user_item)
                else:
                    raise Http404()

                first_user = User.objects.get(id=request_item.from_user.id)
                second_user = User.objects.get(id=request_item.to_user.id)
                first_user.profile.friends.add(second_user)
                second_user.profile.friends.add(first_user)

                request_item.delete()

                return FriendsViews.get_render(request, {'c_user': request.user})

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            raise Http404()

    @staticmethod
    def cancel_request(request, user_id):
        """
        Method for canceling request
        """
        if request.method == 'POST':
            user_item = get_object_or_404(User, id=user_id)

            if FriendshipRequest.objects.filter(from_user=user_item, to_user=request.user).exists():
                request_item = FriendshipRequest.objects.get(
                    from_user=user_item, to_user=request.user)
            elif FriendshipRequest.objects.filter(from_user=request.user, to_user=user_item).exists():
                request_item = FriendshipRequest.objects.get(
                    from_user=request.user, to_user=user_item)
            else:
                raise Http404()

            request_item.delete()

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()

    @staticmethod
    def remove_friend(request, user_id) -> redirect:
        """
        Remove_friend view
        :param request: request
        :param user_id: id
        :return: redirect
        """
        if request.method == 'POST':
            user_item = get_object_or_404(User, id=user_id)

            if user_item in request.user.profile.friends.all():
                request.user.profile.friends.remove(user_item)
                user_item.profile.friends.remove(request.user)
            else:
                raise Http404()

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()

    @staticmethod
    def blacklist_add(request, user_id):
        """
        Blacklist_add view
        :param request: request
        :param user_id: id
        """

        if request.method == 'POST':
            user_for_blacklist = get_object_or_404(User, id=user_id)

            if user_for_blacklist in request.user.profile.friends.all():
                FriendsViews.remove_friend(request, user_id)

            request.user.profile.blacklist.add(user_for_blacklist)
            request.user.save()

            return FriendsViews.get_render(request, {'c_user': request.user})
        raise Http404()

    @staticmethod
    def blacklist_remove(request, user_id):
        """
        Blacklist_remove view
        :param request: request
        :param user_id: id
        """
        if request.method == 'POST':
            user_to_remove = get_object_or_404(User, id=user_id)

            request.user.profile.blacklist.remove(user_to_remove)

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()
