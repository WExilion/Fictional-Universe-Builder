from django.core.validators import MinLengthValidator
from django.db.models import Q
from django.utils.text import slugify
from rest_framework import serializers

from common.validators import GenreNameValidator
from universes.models import Universe, Genre


class UniverseSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Genre.objects.all(),
        required=False,
    )
    new_genre = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=50,
        validators=[
            GenreNameValidator,
            MinLengthValidator(limit_value=3, message="Genre must be at least 3 characters long."),
        ],
    )


    class Meta:
        model = Universe
        fields = [
            'id',
            'name',
            'slug',
            'owner',
            'owner_username',
            'image_url',
            'description',
            'genres',
            'new_genre',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'owner', 'owner_username', 'created_at', 'updated_at']

    def validate_name(self, name):
        name = name.strip()
        generated_slug = slugify(name)

        if not generated_slug:
            raise serializers.ValidationError(
                "Universe name must contain Latin letters."
            )

        queryset = Universe.objects.filter(
            Q(name__iexact=name) | Q(slug=generated_slug)
        )

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        duplicate = queryset.first()

        if duplicate:
            if duplicate.name.lower() == name.lower():
                raise serializers.ValidationError(
                    f"A universe named '{name}' already exists."
                )

            raise serializers.ValidationError(
                f"A universe with a similar name to '{duplicate.name}' already exists. "
                f"Names like Universe Second and Universe-Second, or Galaxy's Edge and Galaxys Edge are considered the same."
            )

        return name


    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        if self.partial and 'genres' not in attrs and 'new_genre' not in attrs:
            return attrs

        if 'genres' in attrs:
            genres = list(attrs.get('genres', []))
        elif instance is not None:
            genres = list(instance.genres.all())
        else:
            genres = []

        new_genre = attrs.get('new_genre', '').strip()
        attrs['new_genre'] = new_genre

        if not genres and not new_genre:
            raise serializers.ValidationError("Select at least one genre or add a new one to define your universe.")

        if new_genre:
            genres_lower = [g.name.lower() for g in genres]
            if new_genre.lower() in genres_lower:  # noqa
                raise serializers.ValidationError(f"'{new_genre}' is already selected above — no need to add it again.")
            elif Genre.objects.filter(name__iexact=new_genre).exists():
                raise serializers.ValidationError(f"'{new_genre}' already exists in the genres — select it from the list above.")


        total = len(genres) + (1 if new_genre else 0)
        if total > 6:
            raise serializers.ValidationError(f"You selected {total} genres — choose up to 6 genres in total, including a new custom genre.")

        return attrs

    def create(self, validated_data):
        genres = list(validated_data.pop('genres', []))
        new_genre = validated_data.pop('new_genre', '')

        universe = Universe.objects.create(**validated_data)

        if new_genre:
            genre_obj, _ = Genre.objects.get_or_create(name=new_genre)
            genres.append(genre_obj)

        if genres:
            universe.genres.set(genres) # noqa

        return universe


    def update(self, instance, validated_data):
        genres_provided = 'genres' in validated_data
        genres = list(validated_data.pop('genres', [])) if genres_provided else list(instance.genres.all())
        new_genre = validated_data.pop('new_genre', '')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if new_genre:
            genre_obj, _ = Genre.objects.get_or_create(name=new_genre)
            if genre_obj not in genres:
                genres.append(genre_obj)

        if len(genres) > 6:
            raise serializers.ValidationError(f"You selected {len(genres)} genres — choose up to 6 genres in total, including a new custom genre.")

        if genres_provided or new_genre:
            instance.genres.set(genres)

        return instance


