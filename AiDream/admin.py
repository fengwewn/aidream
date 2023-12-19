from django.contrib import admin

# Register your models here.
from AiDream.models import embeddingInfo, generateInfo

class embeddingInfoAdmin(admin.ModelAdmin):
    list_display = ['embedding_id','embedding_name','embedding_creator','embedding_status','embedding_time']
    search_fields = list_display

admin.site.register(embeddingInfo,embeddingInfoAdmin)

class generateInfoAdmin(admin.ModelAdmin):
    list_display = ["generate_id", "generate_keyword", "generate_opposite_keyword", "generate_width", "generate_height", "generate_round", "generate_num", "generate_art_width", "generate_art_step", "generate_seed", "generate_creator", "generate_status", "generate_time"]
    search_fields = list_display

admin.site.register(generateInfo,generateInfoAdmin)

