from django.utils import timezone
from django.core.validators import validate_email
from rest_framework_mongoengine import serializers
from rest_framework.exceptions import ValidationError

from listings.models.report_issue import ReportIssue
from listings.models.review import Review


class ReportIssueSerializer(serializers.DocumentSerializer):
    """
    handles the serialization for report_issue
    """

    class Meta:
        model = ReportIssue
        fields = "__all__"

    def validate(self, data):
        validate_email(data.get("email"))
        user = self.context["request"].user
        data["user_id"] = user.id
        data["created_at"] = timezone.now()

        return data

    def create(self, validated_data):
        return ReportIssue.objects.create(**validated_data)


class ReviewSerializer(serializers.DocumentSerializer):
    """
    handles the serialization for review
    """

    class Meta:
        model = Review
        fields = "__all__"

    def validate(self, data):
        required_fields = ["Hate", "Dislike", "Neutral", "Like", "Love"]
        user = self.context["request"].user

        if data.get("review") not in required_fields:
            raise ValidationError(
                {"review": f"review must be {required_fields}"}
            )
        data["user_id"] = user.id
        data["created_at"] = timezone.now()

        return data

    def create(self, validated_data):
        return Review.objects.create(**validated_data)
