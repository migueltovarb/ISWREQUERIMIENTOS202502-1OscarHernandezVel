from django import forms
from django.utils import timezone

# /c:/Users/felip/OneDrive/Documents/Desktop/Ingenieria de Requerimientos/Sistema_de_Gestón_de_Notas_y_Estudiantes/gestion_notas/forms.py

try:
    from .models import Student, Grade, Course
except Exception:
    Student = Grade = Course = None


class GenericArchiveForm(forms.Form):
    """
    Generic archive form for single object operations.
    - object_id: id of the object to archive/unarchive
    - archived: True to mark archived, False to unarchive
    - reason: optional explanation
    - archived_at: optional timestamp override (defaults to now when archiving)
    """
    object_id = forms.CharField(widget=forms.HiddenInput)
    archived = forms.BooleanField(required=False, initial=True, label="Archive this item")
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    archived_at = forms.DateTimeField(required=False, initial=timezone.now)

    def clean_object_id(self):
        oid = self.cleaned_data["object_id"]
        if not oid:
            raise forms.ValidationError("Missing object id.")
        return oid


class BulkArchiveForm(forms.Form):
    """
    Bulk archive/unarchive form.
    If a queryset is passed to __init__ it will create a ModelMultipleChoiceField.
    Otherwise it uses a comma-separated ids string.
    """
    ids = forms.CharField(
        required=False,
        help_text="Comma-separated ids to archive (used when no queryset provided)."
    )
    archived = forms.BooleanField(required=False, initial=True, label="Archive selected items")
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, queryset=None, queryset_label="items", **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = queryset
        if queryset is not None:
            # replace ids field with a multiple choice based on the queryset
            self.fields["ids_qs"] = forms.ModelMultipleChoiceField(
                queryset=queryset,
                required=False,
                label=f"Select {queryset_label} to archive"
            )
            # keep legacy 'ids' for API compatibility
            self.fields["ids"].widget = forms.HiddenInput()


def archive_queryset(queryset, archived=True, by_user=None, reason=None, timestamp=None):
    """
    Simple helper to mark a queryset as archived/unarchived.
    - sets `archived` boolean field if present
    - sets `archived_at` datetime field if present
    - does not raise if fields are missing; returns number of updated rows when possible
    """
    if timestamp is None:
        timestamp = timezone.now()

    # try bulk update if model has fields
    model = getattr(queryset, "model", None)
    if model is not None:
        update_kwargs = {}
        if hasattr(model, "archived"):
            update_kwargs["archived"] = archived
        if hasattr(model, "archived_at"):
            update_kwargs["archived_at"] = timestamp if archived else None
        if update_kwargs:
            return queryset.update(**update_kwargs)

    # fallback: iterate and set attributes
    updated = 0
    for obj in queryset:
        changed = False
        if hasattr(obj, "archived"):
            obj.archived = archived
            changed = True
        if hasattr(obj, "archived_at"):
            obj.archived_at = timestamp if archived else None
            changed = True
        if changed:
            try:
                obj.save()
                updated += 1
            except Exception:
                # skip failing saves
                pass
    return updated


# If models are available, provide ModelForms to simplify CRUD + archive fields.
if Student is not None:
    class StudentForm(forms.ModelForm):
        class Meta:
            model = Student
            # prefer explicit common fields but fall back to all if model differs
            fields = getattr(Student, "FORM_FIELDS", ["first_name", "last_name", "email", "enrollment_date", "archived"])
            # if fields is a callable attr, ensure it's a list/tuple
            if isinstance(fields, str):
                fields = [fields]

if Grade is not None:
    class GradeForm(forms.ModelForm):
        class Meta:
            model = Grade
            fields = getattr(Grade, "FORM_FIELDS", ["student", "course", "score", "date", "archived"])

if Course is not None:
    class CourseForm(forms.ModelForm):
        class Meta:
            model = Course
            fields = getattr(Course, "FORM_FIELDS", ["name", "code", "description", "archived"])