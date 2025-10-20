from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Position, Candidate, Vote
from .forms import PositionForm, CandidateForm, VotingForm, CustomLoginForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q


# Create your views here.
def user_homepage(request):
    return render(request, 'main/user_home.html')

def admin_homepage(request):
    return render(request, 'main/admin_home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def manage_positions(request):
    positions = Position.objects.all()
    return render(request, 'main/manage_positions.html', {'positions': positions})

def register_position(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position_name = form.cleaned_data.get('position_name')
            messages.success(request, f"Position ({position_name}) created successfully!")
            form.save()
            return redirect('manage_positions')
    else:
        form = PositionForm()
    return render(request, 'main/register_position.html', {'form': form})

def manage_candidates(request):
    positions = Position.objects.prefetch_related('candidate_position').all()
    return render(request, 'main/manage_candidates.html', {'positions': positions})

def register_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate_name = form.cleaned_data.get('candidate_name')
            candidate_position = form.cleaned_data.get('candidate_position')
            if Candidate.objects.filter(candidate_name=candidate_name, candidate_position=candidate_position).exists():
                messages.error(request, f"Candidate ({candidate_name}) is already registered for the position ({candidate_position}).")
            else:
                form.save()
                messages.success(request, f"Candidate ({candidate_name}) registered successfully for the position ({candidate_position}).")
                return redirect('manage_candidates')
    else:
        form = CandidateForm()
    return render(request, 'main/register_candidate.html', {'form': form})

def vote_view(request):
    positions = Position.objects.prefetch_related('candidate_position').all()
    has_voted = Vote.objects.filter(voter=request.user).exists()
    if has_voted:
        messages.error(request, "You have already voted. Voting is allowed only once.")
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_homepage')
        else:
            return redirect('user_homepage')
    if request.method == 'POST':
        form = VotingForm(request.POST)
        if form.is_valid():
            for position in positions:
                candidates = position.candidate_position.all()
                for candidate in candidates:
                    choice = form.cleaned_data.get(f'vote_{candidate.id}')
                    Vote.objects.create(
                        voter=request.user,
                        position=position,
                        candidate=candidate,
                        choice=choice
                    )
            messages.success(request, "Your votes have been submitted!")
            if request.user.is_superuser or request.user.is_staff:
                return redirect('admin_homepage')
            else:
                return redirect('user_homepage')
        else:
            messages.error(request, "There was an error with your vote submission. Please vote for every candidate.")
    else:
        form = VotingForm()
    return render(request, 'main/vote.html', {'form': form, 'positions': positions})        

def manage_vote_dashboard(request):
    total_voters = User.objects.count()
    voted_count = Vote.objects.values('voter').distinct().count()
    not_voted_count = total_voters - voted_count
    return render(request, 'main/manage_vote_dashboard.html', {
        'total_voters': total_voters,
        'voted_count': voted_count,
        'not_voted_count': not_voted_count
    })

def voter_list(request):
    voters = User.objects.all()
    return render(request, 'main/voter_list.html', {'voters': voters})

def voted_list(request):
    voted_user_ids = Vote.objects.values_list('voter', flat=True).distinct()
    voted_users = User.objects.filter(id__in=voted_user_ids)
    votes = Vote.objects.select_related('voter', 'candidate', 'position')
    user_votes = {}
    for user in voted_users:
        user_votes[user.id] = list(votes.filter(voter=user))
    return render(request, 'main/voted_list.html', {
        'voted_users': voted_users,
        'user_votes': user_votes,
    })

from django.db.models import Count, Q

def vote_results(request):
    positions = Position.objects.prefetch_related('candidate_position')
    results = []
    for position in positions:
        candidates = position.candidate_position.all()
        candidate_data = []
        for candidate in candidates:
            yes_count = Vote.objects.filter(position=position, candidate=candidate, choice='yes').count()
            no_count = Vote.objects.filter(position=position, candidate=candidate, choice='no').count()
            total = yes_count + no_count
            yes_pct = int((yes_count / total) * 100) if total > 0 else 0
            yes_style = f"width: {yes_pct}%;"
            candidate_data.append({
                'candidate': candidate,
                'yes_count': yes_count,
                'no_count': no_count,
                'total': total,
                'yes_pct': yes_pct,
                'yes_style': yes_style,
            })
        results.append({
            'position': position,
            'candidates': candidate_data,
        })
    return render(request, 'main/vote_results.html', {'results': results})


def not_voted_list(request):
    voted_user_ids = Vote.objects.values_list('voter', flat=True).distinct()
    not_voted_users = User.objects.exclude(id__in=voted_user_ids)
    return render(request, 'main/not_voted_list.html', {'not_voted_users': not_voted_users})

def candidate_voters(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    votes = Vote.objects.filter(candidate=candidate).select_related('voter', 'position')
    voters = [vote.voter for vote in votes]
    return render(request, 'main/candidate_voters.html', {
        'candidate': candidate,
        'votes': votes,
        'voters': voters,
    })


class CustomLoginView(LoginView):
    template_name = 'main/login.html'

    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse_lazy('admin_homepage')
        else:
            return reverse_lazy('user_homepage')
        