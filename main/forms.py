from django import forms
from .models import Position, Candidate, Vote

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_name', 'description']

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['candidate_name', 'photo', 'candidate_position']
        widgets = {
            'candidate_name': forms.Select(attrs={'id': 'id_candidate_name'}),
        }

class VotingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for position in Position.objects.all():
            candidates = Candidate.objects.filter(candidate_position=position)
            for candidate in candidates:
                self.fields[f'vote_{candidate.id}'] = forms.ChoiceField(
                    choices=[('yes', 'Yes'), ('no', 'No')],
                    widget=forms.RadioSelect,
                    label=f"{candidate.candidate_name.first_name} {candidate.candidate_name.last_name}",
                    required=True
                )

class CustomLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)