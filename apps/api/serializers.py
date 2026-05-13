from rest_framework import serializers
from django.db.models import Sum
from apps.accounts.models import CustomUser, Profile
from apps.transactions.models import Transaction, Category
from apps.budgets.models import Budget
from apps.goals.models import SavingsGoal
from apps.ai_engine.models import AIInsight
from apps.core.finance import user_visible_category_queryset


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('currency', 'monthly_income_goal', 'monthly_savings_goal', 'timezone', 'bio')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'profile', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        Profile.objects.get_or_create(user=user)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type', 'icon', 'color', 'is_default')
        read_only_fields = ('id',)


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    tag_list = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = (
            'id', 'transaction_type', 'amount', 'description', 'notes',
            'date', 'category', 'category_name', 'category_color',
            'tags', 'tag_list', 'recurrence', 'is_recurring', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive.')
        return value

    def validate_category(self, value):
        request = self.context.get('request')
        if value and request and not user_visible_category_queryset(request.user).filter(pk=value.pk).exists():
            raise serializers.ValidationError('Invalid category for this user.')
        return value


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Use SerializerMethodField to read pre-annotated values — avoids N+1
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    utilization_percent = serializers.SerializerMethodField()
    is_exceeded = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            'id', 'category', 'category_name', 'amount', 'month', 'year',
            'alert_threshold', 'spent', 'remaining', 'utilization_percent', 'is_exceeded',
        )
        read_only_fields = ('id',)

    def get_spent(self, obj):
        return float(obj.spent)

    def get_remaining(self, obj):
        return float(obj.remaining)

    def get_utilization_percent(self, obj):
        return obj.utilization_percent

    def get_is_exceeded(self, obj):
        return obj.is_exceeded

    def validate_category(self, value):
        request = self.context.get('request')
        if value.category_type != 'expense':
            raise serializers.ValidationError('Budgets can only use expense categories.')
        if request and not user_visible_category_queryset(request.user).filter(pk=value.pk).exists():
            raise serializers.ValidationError('Invalid category for this user.')
        return value

    def validate_alert_threshold(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError('Alert threshold must be between 1 and 100.')
        return value


class SavingsGoalSerializer(serializers.ModelSerializer):
    progress_percent = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()

    class Meta:
        model = SavingsGoal
        fields = (
            'id', 'name', 'description', 'target_amount', 'current_amount',
            'target_date', 'icon', 'color', 'status',
            'progress_percent', 'remaining_amount', 'is_completed', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = ('id', 'insight_type', 'title', 'message', 'severity', 'is_read', 'data', 'created_at')
        read_only_fields = ('id', 'created_at')
