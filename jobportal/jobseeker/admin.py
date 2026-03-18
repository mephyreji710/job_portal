from django.contrib import admin
from .models import JobSeekerProfile, Skill, Education, Experience, Certification


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'is_available',
                    'get_completeness', 'updated_at')
    list_filter = ('is_available', 'preferred_job_type', 'gender')
    search_fields = ('user__email', 'user__first_name', 'headline', 'location')
    inlines = [SkillInline, EducationInline, ExperienceInline, CertificationInline]

    def get_completeness(self, obj):
        return f"{obj.get_completeness()}%"
    get_completeness.short_description = 'Profile %'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'proficiency', 'years_of_experience')
    list_filter = ('proficiency',)
    search_fields = ('name', 'profile__user__email')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('field_of_study', 'degree', 'institution', 'start_year', 'end_year')
    search_fields = ('institution', 'field_of_study', 'profile__user__email')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'employment_type', 'start_date', 'is_current')
    list_filter = ('employment_type', 'is_current')
    search_fields = ('job_title', 'company', 'profile__user__email')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuing_organization', 'issue_date', 'does_not_expire')
    search_fields = ('name', 'issuing_organization', 'profile__user__email')
