from django.contrib import admin

from .models import Channel, Message, MessageReaction, ReadReceipt


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ["author", "content", "is_deleted", "created_at"]
    readonly_fields = ["created_at"]
    show_change_link = True


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "channel_type", "is_archived", "created_at"]
    list_filter = ["channel_type", "is_archived", "organization"]
    search_fields = ["name", "slug"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["pk", "channel", "author", "is_deleted", "is_edited", "created_at"]
    list_filter = ["is_deleted", "is_edited"]
    search_fields = ["content", "author__email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ["message", "user", "emoji", "created_at"]
    search_fields = ["emoji", "user__email"]


@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ["channel", "user", "last_read_at"]
