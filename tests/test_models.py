import pytest
import os
import tempfile
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.staff import Staff
from app.models.project import Project
from app.models.payment import Payment
from app.models.research_field import ResearchField

class TestUserModel:
    def setup_method(self):
        """Setup test database"""
        with app.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up after tests"""
        with app.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_creation(self):
        """Test user creation"""
        with app.app.app_context():
            # Test creating a user
            user = User(
                name='Test User',
                email='test@example.com',
                password='testpassword123'
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Test user attributes
            assert user.name == 'Test User'
            assert user.email == 'test@example.com'
            assert user.role == 'user'
            assert user.status == 'active'
            assert user.email_verified == False
            assert user.created_at is not None
            user_id = user.id
            
            # Test password hashing
            assert user.check_password('testpassword123')
            assert not user.check_password('wrongpassword')
            
            # Test token generation
            tokens = user.generate_tokens()
            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
            assert tokens['token_type'] == 'Bearer'
            
            return user
    
    def test_user_validation(self):
        """Test user validation"""
        with app.app.app_context():
            # Test email validation
            with pytest.raises(ValueError):
                User.create_user('', 'test@example.com', 'password123')
            
            with pytest.raises(ValueError):
                User.create_user('Test User', 'invalid-email', 'password123')
            
            # Test password validation
            with pytest.raises(ValueError):
                User.create_user('Test User', 'test@example.com', 'short')
            
            # Test name validation
            with pytest.raises(ValueError):
                User.create_user('', 'test@example.com', 'testpassword123')
            
            # Test role validation
            with pytest.raises(ValueError):
                User.create_user('Test User', 'test@example.com', 'testpassword123', 'invalid_role')
    
    def test_user_methods(self):
        """Test user methods"""
        with app.app_context():
            user = User.create_user('Test User', 'test@example.com', 'testpassword123')
            
            # Test profile update
            user.update_profile(phone='1234567890', avatar='avatar.jpg')
            assert user.phone == '1234567890'
            assert user.avatar == 'avatar.jpg'
            
            # Test password change
            user.change_password('newpassword123')
            assert user.check_password('newpassword123')
            
            # Test user deactivation
            user.deactivate()
            assert user.status == 'inactive'
            
            # Test user reactivation
            user.activate()
            assert user.status == 'active'
            
            # Test user deletion
            user.delete()
            
            # Verify user is deleted
            deleted_user = User.find_by_id(user_id)
            assert deleted_user is None
            
            return user
    
    def test_user_relationships(self):
        """Test user relationships"""
        with app.app_context():
            # Create user
            user = User.create_user('Test User', 'test@example.com', 'testpassword123')
            
            # Test project relationship
            assert len(user.projects) == 0
            
            # Create projects for user
            from app.models.project import Project
            project1 = Project(
                title='Test Project 1',
                research_field='computer-science',
                user_id=user.id
            )
            project2 = Project(
                title='Test Project 2',
                research_field='engineering',
                user_id=user.id
            )
            
            db.session.add(project1)
            db.session.add(project2)
            db.session.commit()
            
            # Verify relationships
            assert len(user.projects) == 2
            assert user.projects[0].title == 'Test Project 1'
            assert user.projects[1].title == 'Test Project 2'
            
            # Clean up
            project1.delete()
            project2.delete()
            user.delete()
            
            return user

class TestStaffModel:
    def setup_method(self):
        """Setup test database"""
        with app.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up after tests"""
        with app.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_staff_creation(self):
        """Test staff creation"""
        with app.app_context():
            # Create user first
            user = User.create_user('Test Staff', 'staff@example.com', 'testpassword123', 'staff')
            
            # Create staff profile
            staff = Staff.create_staff_profile(user.id, 'computer-science', 5)
            
            # Test staff attributes
            assert staff.user_id == user.id
            assert staff.specialization == 'computer-science'
            assert staff.experience_years == 5
            assert staff.rating == 0.0
            assert staff.total_projects == 0
            assert staff.completed_projects == 0
            assert staff.availability is True
            
            return staff
    
    def test_staff_methods(self):
        """Test staff methods"""
        with app.app.app_context():
            # Create user and staff
            user = User.create_user('Test Staff', 'staff@example.com', 'testpassword123', 'staff')
            staff = Staff.create_staff_profile(user.id, 'computer-science', 5)
            
            # Test profile update
            staff.update_profile(
                qualification='PhD Computer Science',
                bio='Test bio',
                hourly_rate=50.0
            )
            
            assert staff.qualification == 'PhD Computer Science'
            assert staff.bio == 'Test bio'
            assert staff.hourly_rate == 50.0
            
            # Test availability
            staff.set_availability(False)
            assert not staff.availability
            
            # Test performance update
            staff.update_rating()
            assert staff.rating >= 0.0
            
            # Test project assignment
            from app.models.project import Project
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id
            )
            
            staff.assign_project(project)
            assert project.assigned_staff_id == staff.id
            assert project.status == 'in_progress'
            
            # Test project completion
            staff.complete_project(project)
            assert project.status == 'completed'
            assert staff.completed_projects == 1
            assert staff.total_projects == 1
            
            # Clean up
            project.delete()
            staff.delete()
            user.delete()
            
            return staff
    
    def test_staff_performance(self):
        """Test staff performance metrics"""
        with app.app_context():
            # Create user and staff
            user = User.create_user('Test Staff', 'staff@example.com', 'testpassword123', 'staff')
            staff = Staff.create_staff_profile(user.id, 'computer-science', 5)
            
            # Test performance calculation
            staff.total_projects = 5
            staff.completed_projects = 3
            staff.update_rating()
            
            assert staff.total_projects == 5
            assert staff.completed_projects == 3
            assert staff.rating >= 0.0
            assert staff.get_performance_stats()['completion_rate'] == 60.0
            
            return staff

class TestProjectModel:
    def setup_method(self):
        """Setup test database"""
        with app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_project_creation(self):
        """Test project creation"""
        with app.app_context():
            # Create user
            user = User.create_user('Test User', 'user@example.com', 'testpassword123', 'user')
            
            # Create project
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id,
                price=100.0,
                currency='USD'
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Test project attributes
            assert project.title == 'Test Project'
            assert project.research_field == 'computer-science'
            assert project.status == 'pending'
            assert project.price == 100.0
            assert project.currency == 'USD'
            assert project.user_id == user.id
            
            return project
    
    def test_project_methods(self):
        """Test project methods"""
        with app.app.app_context():
            # Create user and project
            user = user = User.create_user('Test User', 'user@example.com', 'testpassword123', 'user')
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id,
                price=100.0,
                currency='USD'
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Test project description
            description_data = {
                'objectives': 'Test objectives',
                'methodology': 'Test methodology',
                'expected_outcomes': 'Test outcomes',
                'timeline': 'Test timeline'
            }
            
            project.set_description_dict(description_data)
            
            # Test project status updates
            project.update_status('in_progress')
            assert project.status == 'in_progress'
            
            project.update_status('completed')
            assert project.status == 'completed'
            
            # Test project deletion
            project.delete()
            
            # Verify project is deleted
            deleted_project = Project.find_by_id(project.id)
            assert deleted_project is None
            
            return project
    
    def test_project_validation(self):
        """Test project validation"""
        with app.app.app_context():
            # Test title validation
            with pytest.raises(ValueError):
                Project(
                    title='',  # Empty title
                    research_field='computer-science',
                    user_id=1
                )
            
            # Test research field validation
            with pytest.raises(ValueError):
                Project(
                    title='Test Project',
                    research_field='invalid-field',
                    user_id=1
                )
            
            # Test price validation
            with pytest.raises(ValueError):
                Project(
                    title='Test Project',
                    research_field='computer-science',
                    user_id=1,
                    price=-10.0  # Negative price
                )
            
            # Test priority validation
            with pytest.raises(ValueError):
                Project(
                    title='Test Project',
                    research_field='computer-science',
                    user_id=1,
                    priority='invalid-priority'
                )
            
            return True
    
    def test_project_relationships(self):
        """Test project relationships"""
        with app.app.app_context():
            # Create user and project
            user = User.create_user('Test User', 'user@example.com', 'testpassword123', 'user')
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id,
                price=100.0
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Test user relationship
            assert project.user_id == user.id
            assert project.user.name == 'Test User'
            
            return project

class TestPaymentModel:
    def setup_method(self):
        """Setup test database"""
        with app.app_app_context():
            db.create_all()
    
    def teardown_method(self):
        """Clean up after tests"""
        with app.app_app_context():
            db.session.remove()
            db.drop_all()
    
    def test_payment_creation(self):
        """Test payment creation"""
        with app.app_app_context():
            # Create user and project
            user = User.create_user('Test User', 'user@example.com', 'testpassword123', 'user')
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id,
                price=100.0,
                currency='USD'
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Create payment
            payment = Payment(
                transaction_id='test-transaction-123',
                user_id=user.id,
                project_id=project.id,
                amount=100.0,
                currency='USD',
                status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Test payment attributes
            assert payment.transaction_id == 'test-transaction-123'
            assert payment.user_id == user.id
            assert payment.project_id == project.id
            assert payment.amount == 100.0
            assert payment.currency == 'USD'
            assert payment.status == 'pending'
            
            return payment
    
    def test_payment_methods(self):
        """Test payment methods"""
        with app.app_app_context():
            # Create user, project, and payment
            user = User.create_user('Test User', 'user@example.com', 'testpassword123', 'user')
            project = Project(
                title='Test Project',
                research_field='computer-science',
                user_id=user.id,
                price=100.0,
                currency='USD'
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Test payment processing
            payment = Payment(
                transaction_id='test-transaction-123',
                user_id=user.id,
                project_id=project.id,
                amount=100.0,
                currency='USD',
                status='completed'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Test payment completion
            payment.complete_payment()
            assert payment.status == 'completed'
            
            # Test payment refund
            payment.refund_payment('Test refund')
            assert payment.status == 'refunded'
            
            return payment

# Create instance
test_models = TestUserModel()
test_staff = TestStaffModel()
test_project = TestProjectModel()
test_payment = TestPaymentModel()
