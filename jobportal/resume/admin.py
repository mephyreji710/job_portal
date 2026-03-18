from django.contrib import admin
from .models import Resume, ParsedResume, ExtractedKeyword


class ExtractedKeywordInline(admin.TabularInline):
    model = ExtractedKeyword
    readonly_fields = ('word', 'frequency', 'is_skill', 'category')
    extra = 0
    max_num = 0
    can_delete = False


class ParsedResumeInline(admin.StackedInline):
    model = ParsedResume
    readonly_fields = (
        'parsed_at', 'extracted_skills', 'extracted_keywords',
        'total_words', 'total_keywords', 'tech_skill_count', 'soft_skill_count',
        'estimated_experience_years', 'education_level',
        'extracted_name', 'extracted_email', 'extracted_phone',
        'extracted_linkedin', 'extracted_github', 'extracted_website',
    )
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 'user', 'file_type',
        'get_file_size_display', 'status', 'is_primary', 'uploaded_at',
    )
    list_filter  = ('status', 'file_type', 'is_primary')
    search_fields = ('original_filename', 'user__email')
    readonly_fields = ('uploaded_at', 'parsed_at', 'raw_text', 'file_size', 'original_filename')
    inlines = [ParsedResumeInline]


@admin.register(ParsedResume)
class ParsedResumeAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'education_level', 'estimated_experience_years',
        'tech_skill_count', 'soft_skill_count', 'total_words', 'parsed_at',
    )
    readonly_fields = ('parsed_at',)
    inlines = [ExtractedKeywordInline]


@admin.register(ExtractedKeyword)
class ExtractedKeywordAdmin(admin.ModelAdmin):
    list_display  = ('word', 'frequency', 'category', 'is_skill', 'parsed_resume')
    list_filter   = ('category', 'is_skill')
    search_fields = ('word',)
