"""
Management command to create sample data for the booking system.
Based on VALclean services from https://valclean.uk/booking/
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal

from services.models import Category, Service
from staff.models import Staff, StaffScheduleItem, StaffService
from customers.models import Customer
from appointments.models import Appointment, CustomerAppointment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the booking system (staff, users, services, appointments)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create categories
        categories = self.create_categories()
        
        # Create services
        services = self.create_services(categories)
        
        # Create staff
        staff_members = self.create_staff()
        
        # Link staff to services
        self.link_staff_to_services(staff_members, services)
        
        # Create users and customers
        users_customers = self.create_users_and_customers()
        
        # Create appointments
        self.create_appointments(staff_members, services, users_customers)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(categories)} categories'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(services)} services'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(staff_members)} staff members'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(users_customers)} users/customers'))
        self.stdout.write(self.style.SUCCESS(f'  - Multiple appointments'))

    def create_categories(self):
        """Create service categories."""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {'name': 'Cleaning Services', 'description': 'Professional cleaning services for your home'},
            {'name': 'Maintenance Services', 'description': 'Handyman and maintenance services'},
            {'name': 'Green Spaces', 'description': 'Garden and outdoor maintenance'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True,
                    'visibility': 'public',
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  ✓ Created category: {category.name}')
        
        return categories

    def create_services(self, categories):
        """Create services based on VALclean website."""
        self.stdout.write('Creating services...')
        
        cleaning_cat = categories[0]
        maintenance_cat = categories[1]
        green_cat = categories[2]
        
        services_data = [
            {
                'title': 'Basic Home Cleaning',
                'category': cleaning_cat,
                'description': 'Standard home cleaning service including dusting, vacuuming, mopping, and bathroom cleaning.',
                'duration': 120,  # 2 hours
                'price': Decimal('45.00'),
                'capacity': 1,
                'color': '#4CAF50',
            },
            {
                'title': 'Duo Automatic Home Cleaning Service',
                'category': cleaning_cat,
                'description': 'Premium cleaning service with two cleaners for faster and more thorough cleaning.',
                'duration': 180,  # 3 hours
                'price': Decimal('85.00'),
                'capacity': 2,
                'color': '#2196F3',
            },
            {
                'title': 'Post Renovation Cleaning',
                'category': cleaning_cat,
                'description': 'Deep cleaning service after renovation work, including dust removal and thorough sanitization.',
                'duration': 240,  # 4 hours
                'price': Decimal('120.00'),
                'capacity': 2,
                'color': '#FF9800',
            },
            {
                'title': 'Move In/Out Service',
                'category': cleaning_cat,
                'description': 'Comprehensive cleaning service for moving in or out of a property.',
                'duration': 300,  # 5 hours
                'price': Decimal('150.00'),
                'capacity': 2,
                'color': '#9C27B0',
            },
            {
                'title': 'Window Cleaning',
                'category': cleaning_cat,
                'description': 'Professional window cleaning service for interior and exterior windows.',
                'duration': 90,  # 1.5 hours
                'price': Decimal('35.00'),
                'capacity': 1,
                'color': '#00BCD4',
            },
            {
                'title': 'Handyman Service',
                'category': maintenance_cat,
                'description': 'General handyman services including repairs, installations, and maintenance tasks.',
                'duration': 120,  # 2 hours
                'price': Decimal('60.00'),
                'capacity': 1,
                'color': '#F44336',
            },
            {
                'title': 'Green Spaces Maintenance',
                'category': green_cat,
                'description': 'Garden maintenance including mowing, trimming, weeding, and general garden care.',
                'duration': 180,  # 3 hours
                'price': Decimal('70.00'),
                'capacity': 1,
                'color': '#8BC34A',
            },
        ]
        
        services = []
        for idx, service_data in enumerate(services_data):
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults={
                    'category': service_data['category'],
                    'description': service_data['description'],
                    'duration': service_data['duration'],
                    'price': service_data['price'],
                    'capacity': service_data['capacity'],
                    'color': service_data['color'],
                    'is_active': True,
                    'visibility': 'public',
                    'position': idx,
                }
            )
            services.append(service)
            if created:
                self.stdout.write(f'  ✓ Created service: {service.title} (£{service.price})')
        
        return services

    def create_staff(self):
        """Create staff members."""
        self.stdout.write('Creating staff members...')
        
        staff_data = [
            {
                'full_name': 'Sarah Johnson',
                'email': 'sarah.johnson@valclean.uk',
                'phone': '07493465560',
                'info': 'Experienced cleaning professional with 5+ years in the industry. Specializes in deep cleaning and post-renovation services.',
            },
            {
                'full_name': 'Michael Brown',
                'email': 'michael.brown@valclean.uk',
                'phone': '07493465561',
                'info': 'Skilled handyman and maintenance specialist. Expert in repairs, installations, and garden maintenance.',
            },
            {
                'full_name': 'Emma Wilson',
                'email': 'emma.wilson@valclean.uk',
                'phone': '07493465562',
                'info': 'Professional cleaner specializing in regular home cleaning and window cleaning services.',
            },
        ]
        
        staff_members = []
        for idx, staff_info in enumerate(staff_data):
            staff, created = Staff.objects.get_or_create(
                email=staff_info['email'],
                defaults={
                    'full_name': staff_info['full_name'],
                    'phone': staff_info['phone'],
                    'info': staff_info['info'],
                    'is_active': True,
                    'visibility': 'public',
                    'position': idx,
                }
            )
            staff_members.append(staff)
            
            if created:
                self.stdout.write(f'  ✓ Created staff: {staff.full_name}')
                
                # Create schedule for staff (Monday to Friday, 9 AM - 8 PM)
                for day_index in range(5):  # Monday to Friday (0-4)
                    StaffScheduleItem.objects.create(
                        staff=staff,
                        day_index=day_index,
                        start_time=time(9, 0),  # 9:00 AM
                        end_time=time(20, 0),  # 8:00 PM
                        breaks=[
                            {'start': '13:00', 'end': '14:00'},  # Lunch break
                        ]
                    )
                self.stdout.write(f'    ✓ Created schedule (Mon-Fri, 9 AM - 8 PM)')
        
        return staff_members

    def link_staff_to_services(self, staff_members, services):
        """Link staff to services they can provide."""
        self.stdout.write('Linking staff to services...')
        
        # Sarah - Cleaning services
        cleaning_services = [s for s in services if s.category.name == 'Cleaning Services']
        for service in cleaning_services:
            StaffService.objects.get_or_create(
                staff=staff_members[0],
                service=service,
                defaults={
                    'price': service.price,
                    'capacity': service.capacity,
                }
            )
        
        # Michael - Maintenance and Green Spaces
        maintenance_services = [s for s in services if s.category.name in ['Maintenance Services', 'Green Spaces']]
        for service in maintenance_services:
            StaffService.objects.get_or_create(
                staff=staff_members[1],
                service=service,
                defaults={
                    'price': service.price,
                    'capacity': service.capacity,
                }
            )
        
        # Emma - All cleaning services
        for service in cleaning_services:
            StaffService.objects.get_or_create(
                staff=staff_members[2],
                service=service,
                defaults={
                    'price': service.price,
                    'capacity': service.capacity,
                }
            )
        
        self.stdout.write('  ✓ Linked staff to services')

    def create_users_and_customers(self):
        """Create users and customers."""
        self.stdout.write('Creating users and customers...')
        
        users_data = [
            {
                'username': 'john_smith',
                'email': 'john.smith@example.com',
                'password': 'testpass123',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '07493465570',
                'role': User.ROLE_CUSTOMER,
                'customer_name': 'John Smith',
                'address_line1': '12 Oak Tree Road',
                'city': 'Yelverton',
                'county': 'Devon',
                'postcode': 'PL20 6BN',
            },
            {
                'username': 'mary_jones',
                'email': 'mary.jones@example.com',
                'password': 'testpass123',
                'first_name': 'Mary',
                'last_name': 'Jones',
                'phone': '07493465571',
                'role': User.ROLE_CUSTOMER,
                'customer_name': 'Mary Jones',
                'address_line1': '45 High Street',
                'city': 'Yelverton',
                'county': 'Devon',
                'postcode': 'PL20 7AB',
            },
            {
                'username': 'david_taylor',
                'email': 'david.taylor@example.com',
                'password': 'testpass123',
                'first_name': 'David',
                'last_name': 'Taylor',
                'phone': '07493465572',
                'role': User.ROLE_CUSTOMER,
                'customer_name': 'David Taylor',
                'address_line1': '8 Meadow View',
                'address_line2': 'Near the Park',
                'city': 'Yelverton',
                'county': 'Devon',
                'postcode': 'PL20 8CD',
            },
        ]
        
        users_customers = []
        for user_data in users_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone': user_data['phone'],
                    'role': user_data['role'],
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'  ✓ Created user: {user.username}')
            
            # Create customer
            customer, created = Customer.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'user': user,
                    'name': user_data['customer_name'],
                    'phone': user_data['phone'],
                    'address_line1': user_data['address_line1'],
                    'address_line2': user_data.get('address_line2', ''),
                    'city': user_data['city'],
                    'county': user_data['county'],
                    'postcode': user_data['postcode'],
                }
            )
            
            if created:
                self.stdout.write(f'    ✓ Created customer: {customer.name}')
            
            users_customers.append((user, customer))
        
        return users_customers

    def create_appointments(self, staff_members, services, users_customers):
        """Create sample appointments."""
        self.stdout.write('Creating appointments...')
        
        now = timezone.now()
        
        # Get services
        basic_cleaning = services[0]  # Basic Home Cleaning
        duo_cleaning = services[1]  # Duo Automatic Home Cleaning
        handyman = services[5]  # Handyman Service
        window_cleaning = services[4]  # Window Cleaning
        
        appointments_data = [
            {
                'staff': staff_members[0],  # Sarah
                'service': basic_cleaning,
                'customer': users_customers[0][1],  # John Smith
                'start_date': now + timedelta(days=2, hours=10),  # 2 days from now at 10 AM
                'status': CustomerAppointment.STATUS_APPROVED,
            },
            {
                'staff': staff_members[2],  # Emma
                'service': window_cleaning,
                'customer': users_customers[1][1],  # Mary Jones
                'start_date': now + timedelta(days=3, hours=14),  # 3 days from now at 2 PM
                'status': CustomerAppointment.STATUS_PENDING,
            },
            {
                'staff': staff_members[1],  # Michael
                'service': handyman,
                'customer': users_customers[2][1],  # David Taylor
                'start_date': now + timedelta(days=5, hours=9),  # 5 days from now at 9 AM
                'status': CustomerAppointment.STATUS_APPROVED,
            },
            {
                'staff': staff_members[0],  # Sarah
                'service': duo_cleaning,
                'customer': users_customers[0][1],  # John Smith
                'start_date': now + timedelta(days=7, hours=11),  # 7 days from now at 11 AM
                'status': CustomerAppointment.STATUS_PENDING,
            },
            {
                'staff': staff_members[2],  # Emma
                'service': basic_cleaning,
                'customer': users_customers[1][1],  # Mary Jones
                'start_date': now + timedelta(days=10, hours=13),  # 10 days from now at 1 PM
                'status': CustomerAppointment.STATUS_APPROVED,
            },
        ]
        
        for appt_data in appointments_data:
            # Calculate end date
            start_date = appt_data['start_date']
            end_date = start_date + timedelta(minutes=appt_data['service'].duration)
            
            # Create appointment
            appointment = Appointment.objects.create(
                staff=appt_data['staff'],
                service=appt_data['service'],
                start_date=start_date,
                end_date=end_date,
            )
            
            # Create customer appointment
            customer_appointment = CustomerAppointment.objects.create(
                customer=appt_data['customer'],
                appointment=appointment,
                number_of_persons=1,
                status=appt_data['status'],
            )
            
            self.stdout.write(
                f'  ✓ Created appointment: {appt_data["customer"].name} - '
                f'{appt_data["service"].title} with {appt_data["staff"].full_name} '
                f'on {start_date.strftime("%Y-%m-%d %H:%M")}'
            )
        
        self.stdout.write(f'  ✓ Created {len(appointments_data)} appointments')

