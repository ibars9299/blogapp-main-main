from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Movie, Series, Book, UserContent, Post, Comment, User, Profile, Follow, Notification
from django.http import JsonResponse
import json

# Create your views here.

def index(request):
    category = request.GET.get('category')
    view_type = request.GET.get('view', 'content')
    
    context = {
        'category': category,
        'view_type': view_type,
    }
    
    if view_type == 'posts':
        # Gönderileri filtrele
        posts = Post.objects.select_related(
            'movie', 'series', 'book', 'user', 'user__profile'
        ).prefetch_related('likes', 'comments').order_by('-created_at')
        
        # Kategori filtreleme
        if category == 'movies':
            posts = posts.filter(movie__isnull=False)
        elif category == 'series':
            posts = posts.filter(series__isnull=False)
        elif category == 'books':
            posts = posts.filter(book__isnull=False)
        
        context['posts'] = posts
        
    else:  # content view
        # İçerikleri filtrele
        movies = Movie.objects.all()
        series = Series.objects.all()
        books = Book.objects.all()
        
        if category == 'movies':
            content = movies
        elif category == 'series':
            content = series
        elif category == 'books':
            content = books
        else:
            content = list(movies) + list(series) + list(books)
        
        # Kullanıcının izleme/okuma durumunu kontrol et
        if request.user.is_authenticated:
            for item in content:
                if isinstance(item, Movie) or isinstance(item, Series):
                    user_content = UserContent.objects.filter(
                        user=request.user,
                        movie=item if isinstance(item, Movie) else None,
                        series=item if isinstance(item, Series) else None
                    ).first()
                    item.is_watched = user_content.watched_read if user_content else False
                elif isinstance(item, Book):
                    user_content = UserContent.objects.filter(
                        user=request.user,
                        book=item
                    ).first()
                    item.is_read = user_content.watched_read if user_content else False
        
        context['content'] = content
    
    return render(request, 'blog/index.html', context)
def movies(request):
    return render(request, 'blog/movies.html')
def series(request):
    return render(request, 'blog/series.html')
def books(request):
    return render(request, 'blog/books.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog:index')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Hoş geldiniz, {username}!')
                return redirect('blog:index')
            else:
                messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('blog:index')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hesabınız oluşturuldu! Hoş geldiniz, {username}!')
            return redirect('blog:index')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('blog:index')

@login_required
def toggle_watched(request):
    data = json.loads(request.body)
    content_type = data.get('type')
    content_id = data.get('id')
    
    try:
        if content_type == 'movie':
            content = Movie.objects.get(id=content_id)
        else:  # series
            content = Series.objects.get(id=content_id)
            
        user_content, created = UserContent.objects.get_or_create(
            user=request.user,
            movie=content if content_type == 'movie' else None,
            series=content if content_type == 'series' else None
        )
        
        user_content.watched_read = not user_content.watched_read
        user_content.save()
        
        return JsonResponse({
            'success': True,
            'status': user_content.watched_read
        })
    except (Movie.DoesNotExist, Series.DoesNotExist):
        return JsonResponse({'success': False}, status=404)

@login_required
def toggle_read(request):
    data = json.loads(request.body)
    book_id = data.get('id')
    
    try:
        book = Book.objects.get(id=book_id)
        user_content, created = UserContent.objects.get_or_create(
            user=request.user,
            book=book
        )
        
        user_content.watched_read = not user_content.watched_read
        user_content.save()
        
        return JsonResponse({
            'success': True,
            'status': user_content.watched_read
        })
    except Book.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def create_post(request):
    content_type = request.GET.get('type')
    content_id = request.GET.get('id')
    
    try:
        # İçeriği al
        if content_type == 'movie':
            content = Movie.objects.get(id=content_id)
        elif content_type == 'series':
            content = Series.objects.get(id=content_id)
        else:
            content = Book.objects.get(id=content_id)
        
        if request.method == 'POST':
            post = Post(
                user=request.user,
                content=request.POST.get('content'),
                rating=request.POST.get('rating')
            )
            
            # İçerik türüne göre ilişkilendirme
            if content_type == 'movie':
                post.movie = content
            elif content_type == 'series':
                post.series = content
            else:
                post.book = content
                
            post.save()
            
            # İzlendi/Okundu olarak işaretle
            user_content, created = UserContent.objects.get_or_create(
                user=request.user,
                movie=content if content_type == 'movie' else None,
                series=content if content_type == 'series' else None,
                book=content if content_type == 'book' else None
            )
            user_content.watched_read = True
            user_content.save()
            
            messages.success(request, 'Gönderiniz başarıyla paylaşıldı!')
            return redirect('blog:index')
        
        return render(request, 'blog/create_post.html', {
            'content': content,
            'content_type': content_type
        })
        
    except (Movie.DoesNotExist, Series.DoesNotExist, Book.DoesNotExist):
        messages.error(request, 'İçerik bulunamadı!')
        return redirect('blog:index')

@login_required
def toggle_like(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        is_liked = request.user in post.likes.all()
        
        if is_liked:
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            if request.user != post.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='like',
                    post=post
                )
        
        # Beğeni durumunu güncelle
        new_is_liked = not is_liked
        likes_count = post.likes.count()
        
        return JsonResponse({
            'success': True,
            'likes_count': likes_count,
            'is_liked': new_is_liked
        })
        
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gönderi bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def add_comment(request, post_id):
    data = json.loads(request.body)
    post = Post.objects.get(id=post_id)
    
    comment = Comment.objects.create(
        post=post,
        user=request.user,
        content=data['content']
    )
    
    # Bildirim oluştur
    if request.user != post.user:  # Kendi gönderisine yorum yaparsa bildirim oluşturma
        Notification.objects.create(
            recipient=post.user,
            sender=request.user,
            notification_type='comment',
            post=post
        )
    
    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'content': comment.content,
        'username': request.user.username,
        'user_image': request.user.profile.image_url,
        'created_at': 'şimdi'
    })

@login_required
def get_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comments = post.comments.select_related('user').prefetch_related('likes').all()
        
        return JsonResponse({
            'success': True,
            'comments': [{
                'id': comment.id,
                'content': comment.content,
                'user': comment.user.username,
                'user_image': comment.user.profile.image_url,
                'created_at': comment.created_at.strftime('%d %b %Y, %H:%M'),
                'likes_count': comment.likes.count(),
                'is_liked': request.user in comment.likes.all(),
                'can_delete': request.user == comment.user or request.user == post.user
            } for comment in comments]
        })
    except Post.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def profile(request, username):
    profile_user = User.objects.get(username=username)  # Profili görüntülenen kullanıcı
    logged_in_user = request.user  # Giriş yapmış kullanıcı
    
    # Profil oluştur (yoksa)
    Profile.objects.get_or_create(user=profile_user)
    
    # İzlenen/okunan içerikleri al
    movies = UserContent.objects.filter(user=profile_user, movie__isnull=False, watched_read=True).select_related('movie')
    series = UserContent.objects.filter(user=profile_user, series__isnull=False, watched_read=True).select_related('series')
    books = UserContent.objects.filter(user=profile_user, book__isnull=False, watched_read=True).select_related('book')
    
    # Kullanıcının gönderilerini al
    posts = Post.objects.filter(user=profile_user).select_related(
        'movie', 'series', 'book'
    ).prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Takip durumunu kontrol et
    is_following = logged_in_user.following.filter(followed=profile_user).exists()
    
    context = {
        'profile_user': profile_user,  # Profili görüntülenen kullanıcı
        'logged_in_user': logged_in_user,  # Giriş yapmış kullanıcı
        'movies': movies,
        'series': series,
        'books': books,
        'posts': posts,
        'movies_count': movies.count(),
        'series_count': series.count(),
        'books_count': books.count(),
        'posts_count': posts.count(),
        'is_own_profile': logged_in_user == profile_user,
        'is_following': is_following,
    }
    
    return render(request, 'blog/profile.html', context)

@login_required
def update_profile_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Eski resmi sil (varsa)
        if profile.image:
            try:
                profile.image.delete(save=False)
            except:
                pass
        
        profile.image = request.FILES['image']
        profile.save()
        
        # Tam URL döndür
        image_url = request.build_absolute_uri(profile.image.url)
        return JsonResponse({
            'success': True,
            'image_url': image_url
        })
    return JsonResponse({'success': False})

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', 'all')
    
    if query:
        if category == 'movies' or category == 'all':
            movies = Movie.objects.filter(title__icontains=query)
        else:
            movies = Movie.objects.none()
            
        if category == 'series' or category == 'all':
            series = Series.objects.filter(title__icontains=query)
        else:
            series = Series.objects.none()
            
        if category == 'books' or category == 'all':
            books = Book.objects.filter(title__icontains=query)
        else:
            books = Book.objects.none()
        
        content = list(movies) + list(series) + list(books)
    else:
        content = []
    
    context = {
        'content': content,
        'query': query,
        'category': category
    }
    
    return render(request, 'blog/search.html', context)

@login_required
def toggle_follow(request, username):
    try:
        user_to_follow = User.objects.get(username=username)
        
        if request.user == user_to_follow:
            return JsonResponse({'error': 'Kendinizi takip edemezsiniz'}, status=400)
        
        follow = Follow.objects.filter(follower=request.user, followed=user_to_follow).first()
        
        if follow:
            # Takibi bırak
            follow.delete()
            is_following = False
        else:
            # Takip et
            Follow.objects.create(follower=request.user, followed=user_to_follow)
            is_following = True
            # Bildirim oluştur
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
        
        followers_count = Follow.objects.filter(followed=user_to_follow).count()
        
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'followers_count': followers_count
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Kullanıcı bulunamadı'}, status=404)

@login_required
def get_notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return JsonResponse({
        'notifications': [{
            'sender': notification.sender.username,
            'type': notification.notification_type,
            'post_id': notification.post.id if notification.post else None,
            'created_at': notification.created_at.strftime('%d %b %Y, %H:%M')
        } for notification in notifications]
    })

@login_required
def mark_notifications_read(request):
    try:
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def get_followers(request, username):
    user = User.objects.get(username=username)
    followers = user.followers.select_related('follower').all()
    return render(request, 'blog/followers.html', {
        'followers': followers,
        'user': user
    })

@login_required
def get_following(request, username):
    user = User.objects.get(username=username)
    following = user.following.select_related('followed').all()
    return render(request, 'blog/following.html', {
        'following': following,
        'user': user
    })

@login_required
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        # Sadece yorum sahibi veya post sahibi yorumu silebilir
        if request.user == comment.user or request.user == comment.post.user:
            comment.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Bu yorumu silme yetkiniz yok'}, status=403)
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yorum bulunamadı'}, status=404)

@login_required
def toggle_comment_like(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        is_liked = request.user in comment.likes.all()
        
        if is_liked:
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
        
        # Beğeni durumunu güncelle
        new_is_liked = not is_liked
        likes_count = comment.likes.count()
        
        return JsonResponse({
            'success': True,
            'likes_count': likes_count,
            'is_liked': new_is_liked
        })
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yorum bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.user == post.user:
            post.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Bu gönderiyi silme yetkiniz yok'}, status=403)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gönderi bulunamadı'}, status=404)

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Film, dizi, kitap ve kullanıcı araması
    movies = Movie.objects.filter(title__icontains=query)[:3]
    series = Series.objects.filter(title__icontains=query)[:3]
    books = Book.objects.filter(title__icontains=query)[:3]
    users = User.objects.filter(username__icontains=query)[:3]
    
    suggestions = {
        'movies': [{'id': m.id, 'title': m.title, 'type': 'movie'} for m in movies],
        'series': [{'id': s.id, 'title': s.title, 'type': 'series'} for s in series],
        'books': [{'id': b.id, 'title': b.title, 'type': 'book'} for b in books],
        'users': [{'username': u.username, 'image': u.profile.image_url} for u in users],
    }
    
    return JsonResponse({'suggestions': suggestions})

@login_required
def post_detail(request, post_id):
    try:
        post = Post.objects.select_related(
            'user', 'movie', 'series', 'book'
        ).prefetch_related('likes', 'comments').get(id=post_id)
        
        context = {
            'post': post,
            'is_liked': request.user in post.likes.all(),
        }
        return render(request, 'blog/post_detail.html', context)
    except Post.DoesNotExist:
        messages.error(request, 'Gönderi bulunamadı.')
        return redirect('blog:index')
