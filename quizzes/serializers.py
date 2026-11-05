from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, QuizAnswer


class ChoicePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choice_text"]


class QuestionPublicSerializer(serializers.ModelSerializer):
    choices = ChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "question_type",
            "marks",
            "order",
            "choices",
        ]


class QuizSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "course_title",
            "lesson",
            "title",
            "description",
            "duration_minutes",
            "total_marks",
            "passing_marks",
            "is_published",
            "questions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_marks",
            "created_at",
            "updated_at",
        ]


class ChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["choice_text", "is_correct"]


class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "question_text",
            "question_type",
            "marks",
            "order",
            "choices",
        ]
        read_only_fields = ["id"]

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "A question must have at least two choices."
            )

        correct_count = sum(
            1 for choice in value if choice.get("is_correct")
        )

        if correct_count != 1:
            raise serializers.ValidationError(
                "Each question must have exactly one correct answer."
            )

        return value

    def create(self, validated_data):
        choices_data = validated_data.pop("choices")
        question = Question.objects.create(**validated_data)

        for choice_data in choices_data:
            Choice.objects.create(
                question=question,
                **choice_data
            )

        return question


class QuizAnswerSubmitSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    selected_choice = serializers.IntegerField()


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(
        source="quiz.title",
        read_only=True
    )

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "attempt_number",
            "score",
            "total_marks",
            "passed",
            "status",
            "started_at",
            "completed_at",
        ]


class QuizAnswerResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(
        source="question.question_text",
        read_only=True
    )

    selected_choice_text = serializers.CharField(
        source="selected_choice.choice_text",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = QuizAnswer
        fields = [
            "id",
            "question",
            "question_text",
            "selected_choice",
            "selected_choice_text",
            "is_correct",
            "marks_obtained",
        ]