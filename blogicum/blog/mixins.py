from django.shortcuts import get_object_or_404, redirect


class PostCommentDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            self.model,
            pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(
            request,
            *args,
            **kwargs)
