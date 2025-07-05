from django.db import models 
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from jeewanjyoti_user.models import CustomUser
from .models import ChatMessage
from .serializers import ChatMessageSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def chat_history(request, user_id):
    """Retrieve chat history between current user and specified user"""
    try:
        other_user = CustomUser.objects.get(id=user_id)
        messages = ChatMessage.objects.filter(
            models.Q(sender=request.user, receiver=other_user) |
            models.Q(sender=other_user, receiver=request.user)
        ).select_related('sender', 'receiver').order_by('timestamp')
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
        
    except CustomUser.DoesNotExist:
        return Response(
            {'detail': 'User not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def send_message(request):
    """Send a new message to another user"""
    data = request.data.copy()
    data['sender'] = request.user.id  # Set sender to current user

    receiver_id = data.get('receiver')
    if not receiver_id:
        return Response(
            {'error': 'Receiver ID is required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Verify receiver exists and is not the same as sender
        if int(receiver_id) == request.user.id:
            return Response(
                {'error': 'Cannot send message to yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        CustomUser.objects.get(id=receiver_id)
    except (CustomUser.DoesNotExist, ValueError):
        return Response(
            {'error': 'Receiver not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ChatMessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def mark_as_seen(request, message_id):
    """Mark a message as seen by the recipient"""
    try:
        message = ChatMessage.objects.get(id=message_id, receiver=request.user)
        if not message.is_seen:
            message.is_seen = True
            message.save(update_fields=['is_seen'])
        return Response({'detail': 'Message marked as seen.'})
    except ChatMessage.DoesNotExist:
        return Response(
            {'detail': 'Message not found or not authorized.'}, 
            status=status.HTTP_404_NOT_FOUND
        )