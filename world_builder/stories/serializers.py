from rest_framework import serializers

from characters.models import Character
from stories.models import Story
from universes.models import Universe


class StorySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    universe_slug = serializers.CharField(source='universe.slug', read_only=True)
    characters = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Character.objects.none(),
        required=False,
    )
    character_names = serializers.SerializerMethodField()
    class Meta:
        model = Story
        fields = [
            'id',
            'title',
            'slug',
            'universe',
            'universe_slug',
            'owner',
            'owner_username',
            'content',
            'is_published',
            'characters',
            'character_names',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'owner', 'owner_username', 'universe_slug', 'created_at', 'updated_at']

    def get_character_names(self, obj):
        return [character.full_name for character in obj.characters.all()]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        story_instance = getattr(self, 'instance', None)
        if not isinstance(story_instance, Story):
            story_instance = None

        if request is None or not request.user.is_authenticated:
            fields['universe'].queryset = Universe.objects.none()
            fields['characters'].queryset = Character.objects.none()
            return fields

        is_moderator = request.user.is_superuser or request.user.groups.filter(name='Moderators').exists()

        if is_moderator and story_instance is not None:
            fields['universe'].queryset = Universe.objects.filter(owner=story_instance.owner)
        else:
            fields['universe'].queryset = Universe.objects.filter(owner=request.user)

        universe_id = request.data.get('universe')
        if story_instance is not None:
            owner = story_instance.owner if is_moderator else request.user
            if universe_id:
                universe = Universe.objects.filter(pk=universe_id, owner=owner).first()
            else:
                universe = story_instance.universe
        else:
            owner = request.user
            universe = Universe.objects.filter(pk=universe_id, owner=owner).first() if universe_id else None

        if universe is not None:
            queryset = Character.objects.filter(owner=owner, universe=universe)
        else:
            queryset = Character.objects.none()

        fields['characters'].queryset = queryset
        return fields


    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        universe = attrs.get('universe')
        if universe is None and instance is not None:
            universe = instance.universe


        if 'characters' in attrs:
            characters = list(attrs.get('characters', []))
        elif instance is not None:
            characters = list(instance.characters.all())
        else:
            characters = []

        if universe and characters:
            invalid_exists = any(character.universe_id != universe.id for character in characters)
            if invalid_exists:
                raise serializers.ValidationError("Selected characters must belong to the selected universe.")
        return attrs











