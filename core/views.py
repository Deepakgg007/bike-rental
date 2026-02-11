from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import datetime
from .models import Bike, Booking
from .forms import BookingForm


def home(request):
    available_bikes = Bike.objects.filter(is_available=True)
    featured_bikes = available_bikes[:3]  # Get first 3 bikes for hero section
    
    context = {
        'available_bikes': available_bikes,
        'featured_bikes': featured_bikes
    }
    return render(request, 'core/index.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for the new user
            from .models import UserProfile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class BikeDetailView(DetailView):
    model = Bike
    template_name = 'core/bike_detail.html'
    context_object_name = 'bike'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bike = self.get_object()
        
        # Add booking form to context
        context['form'] = BookingForm()
        
        # Check if bike is booked for current day
        today = timezone.now().date()
        is_booked_today = Booking.objects.filter(
            bike=bike,
            start_date__date=today,
            status__in=['Pending', 'Active']
        ).exists()
        
        context['is_booked_today'] = is_booked_today
        if is_booked_today:
            context['availability_message'] = 'This bike is already booked for today.'
        else:
            context['availability_message'] = 'This bike is available for booking.'
            
        return context


@login_required
def book_bike(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Check if bike is already booked for these dates
            overlapping_bookings = Booking.objects.filter(
                bike=bike,
                status__in=['Pending', 'Active'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exists()
            
            if overlapping_bookings:
                messages.error(request, 'This bike is already booked for the selected dates.')
            else:
                # Calculate total cost
                days = (end_date - start_date).days + 1
                total_cost = bike.price_per_day * days
                
                # Create booking
                booking = Booking.objects.create(
                    user=request.user,
                    bike=bike,
                    start_date=start_date,
                    end_date=end_date,
                    total_cost=total_cost,
                    status='Pending'
                )
                
                messages.success(request, 'Booking created successfully!')
                return redirect('booking_success')
    
    context = {'bike': bike, 'form': BookingForm()}
    return render(request, 'core/book_bike.html', context)


@login_required
def user_dashboard(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-start_date')
    context = {
        'bookings': user_bookings
    }
    return render(request, 'core/user_dashboard.html', context)
