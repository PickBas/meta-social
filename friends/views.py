"""
Meta social friends views
"""

from simple_search import search_filter

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import Http404

from index.views import MetaSocialView
from user_profile.models import Profile

from .models import FriendshipRequest


class FriendsViews:
    """
    Class containing friends functionality and representation
    """

    @staticmethod
    def get_render(request, context: dict) -> render:
        """
        Friends search. Returns rendered response.
        :param request: request
        :param context: dict
        :return: render
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
        Class FriendsList
        """

        def __init__(self, **kwargs: dict) -> None:
            """
            FriendsList ctor
            :param kwargs: kwargs
            """
            self.template_name = 'friends/friends_list.html'
            self.context = self.get_menu_context('friends', 'Список друзей')
            super().__init__(**kwargs)

        def get(self, request, **kwargs: dict) -> render:
            """
            Processing get request
            :param request: request
            :param kwargs: kwargs
            :return: render
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

        def post(self, request, **kwargs: dict) -> render:
            """
            Processing POST request.
            :param request: request
            :param kwargs: kwargs
            :return: render
            """
            self.context['c_user'] = request.user
            return FriendsViews.get_render(request, self.context)

    class FriendsRequests(MetaSocialView):
        """
        Requests view
        """

        def __init__(self, **kwargs: dict) -> None:
            """
            FriendsRequests ctor
            :param kwargs: kwargs
            """
            self.template_name = 'friends/requests.html'
            super().__init__(**kwargs)

        def get(self, request) -> render:
            """
            Processing GET request
            :param request: request
            :return: render
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

        def __init__(self, **kwargs: dict) -> None:
            """
            FriendsBlacklist ctor
            :param kwargs: kwargs
            """
            self.template_name = 'friends/blacklist.html'
            super().__init__(**kwargs)

        def get(self, request) -> render:
            """
            Friends_blacklist view
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

        def __init__(self, **kwargs: dict) -> None:
            """
            SendFriendshipRequest ctor
            :param kwargs: kwargs
            """
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs: dict) -> redirect:
            """
            Sending friendship request view
            :param request: request
            :param user_id: user's id
            :return: redirect
            """

            self.user_item = get_object_or_404(User, id=kwargs['user_id'])

            if not FriendshipRequest.objects.filter(from_user=self.user_item,
                                                    to_user=request.user).exists():
                if not FriendshipRequest.objects.filter(from_user=request.user,
                                                        to_user=self.user_item).exists():
                    item = FriendshipRequest(
                        from_user=request.user,
                        to_user=self.user_item,
                    )

                    item.save()

                    return FriendsViews.get_render(request, {'c_user': request.user})

            raise Http404()

        def get(self, request, **kwargs: dict) -> Http404:
            """
            Processing GET request. Raising Http404
            :param request: request
            :param kwargs: kwargs
            :return: Http404
            """
            raise Http404()

    class AcceptRequest(MetaSocialView):
        """
        Class for accepting friendship request
        """

        def __init__(self, **kwargs: dict) -> None:
            """
            AcceptRequest ctor
            :param kwargs: kwargs
            """
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs: dict) -> redirect:
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

            raise Http404()

        def get(self, request, **kwargs: dict) -> Http404:
            """
            Processing GET request. Raising Http404
            :param request: request
            :param kwargs: kwargs
            :return: Http404
            """
            raise Http404()

    @staticmethod
    def cancel_request(request, user_id: int) -> render:
        """
        Method for canceling request.
        :raises: Http404 if the request type is GET.
        :param request: request
        :param user_id: user's id
        :return: render
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
    def remove_friend(request, user_id: int) -> render:
        """
        Remove_friend view
        :raises: Http404 if the request type is GET.
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
    def blacklist_add(request, user_id: int) -> render:
        """
        Blacklist_add view.
        :raises: Http404 if the request type is GET.
        :param request: request
        :param user_id: user's id
        :return: render
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
    def blacklist_remove(request, user_id: int) -> render:
        """
        Blacklist_remove view.
        :raises: Http404 if the request type is GET.
        :param request: request
        :param user_id: user's id
        :return: render
        """
        if request.method == 'POST':
            user_to_remove = get_object_or_404(User, id=user_id)

            request.user.profile.blacklist.remove(user_to_remove)

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()
