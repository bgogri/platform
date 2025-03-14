import uuid
import pytest
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db import transaction
import json

from apps.capabilities.talent.models import Skill, Expertise, Person
from apps.capabilities.product_management.models import Product, Challenge, Bounty
from apps.capabilities.security.models import ProductRoleAssignment
from apps.flows.challenge_authoring.services import ChallengeAuthoringService

@pytest.fixture
def user(db):
    """Create a test user with person"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass'
    )
    Person.objects.create(
        user=user,
        full_name="Test User"
    )
    return user

@pytest.fixture
def product(db, user):
    """Create a test product"""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        person=user.person
    )

@pytest.fixture
def valid_challenge_data():
    """Valid challenge creation data"""
    return {
        'title': 'Test Challenge Title',
        'description': 'This is a test challenge description that meets the minimum length requirement for validation.',
        'status': 'draft',
        'priority': 'medium'
    }

@pytest.fixture
def valid_bounties_data(skills):
    return [{
        'title': 'Test Bounty',
        'description': 'Test bounty description',
        'points': 100,
        'skill_id': skills[0].id,
        'expertise_ids': [1, 2]
    }]

@pytest.fixture
def invalid_bounties_data():
    """Invalid bounties data with various validation issues"""
    return [
        {
            'title': '',  # Empty title
            'description': 'Test bounty description',
            'points': 0,  # Invalid points
            'skill': 1,
            'expertise': []  # Empty expertise list
        },
        {
            'title': 'Second Bounty',
            'description': 'Test bounty description',
            'points': 2000,  # Exceeds maximum points
            'skill': 1,
            'expertise': [1]
        }
    ]

@pytest.fixture(autouse=True)
def mock_role_service(mocker):
    """Mock RoleService for all tests"""
    mock = mocker.patch('apps.product_management.flows.challenge_authoring.views.RoleService', autospec=True)
    instance = mock.return_value
    instance.is_product_manager.return_value = True  # Default to True
    return mock

@pytest.fixture
def person(db, django_user_model):
    """Create a test person"""
    # Create a unique username using a UUID
    unique_id = str(uuid.uuid4())[:8]
    username = f'testuser_{unique_id}'
    
    # First create a User instance
    user = django_user_model.objects.create_user(
        username=username,
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )
    
    # Then create the Person instance
    person = Person.objects.create(
        user=user,
        full_name="Test User",
        preferred_name="Test",
        points=0
    )
    
    return person

@pytest.fixture(autouse=True)
def setup_user_person(user, person):
    """Ensure user has a person attribute"""
    user.person = person
    user.save()
    return user

@pytest.fixture
def skills(db):
    """Create test skills"""
    return [
        Skill.objects.create(name='Frontend Development'),
        Skill.objects.create(name='Backend Development')
    ]

@pytest.fixture
def expertise_items(db, skills):
    """Create test expertise items"""
    skill = skills[0]  # Frontend Development skill
    
    # Clear existing expertise
    Expertise.objects.filter(skill=skill).delete()
    
    # Create new expertise items
    expertise_list = []
    for name in ["React", "React Advanced"]:
        expertise = Expertise.objects.create(
            name=name,
            skill=skill,
            selectable=True
        )
        expertise_list.append(expertise)
    
    return expertise_list

@pytest.fixture
def mock_expertise(mocker):
    """Mock expertise data for testing"""
    mock = mocker.patch('apps.product_management.flows.challenge_authoring.services.Expertise')
    mock_instance = mocker.Mock()
    mock_instance.objects.filter.return_value = [
        mocker.Mock(id=1, name='Test Expertise', description='Test Description')
    ]
    mock.return_value = mock_instance
    return mock_instance

@pytest.fixture
def product_manager_role(user, product):
    """Create product manager role for test user"""
    return ProductRoleAssignment.objects.create(
        person=user.person,
        product=product,
        role=ProductRoleAssignment.ProductRoles.MANAGER
    )

@pytest.fixture(autouse=True)
def setup_product_manager(user, product):
    """Setup product manager role for all tests"""
    ProductRoleAssignment.objects.create(
        person=user.person,
        product=product,
        role=ProductRoleAssignment.ProductRoles.MANAGER
    )

@pytest.fixture
def mock_template(mocker):
    mock = mocker.patch('django.template.loader.get_template')
    mock.return_value.render.return_value = ''
    return mock

@pytest.fixture
def expertise_levels(skills):
    """Create test expertise levels"""
    expertise = []
    for skill in skills:
        expertise.extend([
            Expertise.objects.create(
                skill=skill,
                name=f"{skill.name} - Level {i}"
            )
            for i in range(1, 3)
        ])
    return expertise

@pytest.fixture(autouse=True)
def setup_test_data(skills, expertise_levels):
    """Ensure test data is available"""
    pass

@pytest.fixture
def mock_skills(mocker):
    return [
        mocker.Mock(id=1, name='Frontend Development'),
        mocker.Mock(id=2, name='Backend Development')
    ]

@pytest.fixture
def mock_service(mocker):
    mock = mocker.patch('apps.product_management.flows.challenge_authoring.views.ChallengeAuthoringService')
    instance = mock.return_value
    instance.create_challenge.return_value = (True, mocker.Mock(get_absolute_url=lambda: '/test/url'), None)
    return instance

class TestChallengeAuthoringView:
    @pytest.fixture(autouse=True)
    def setup_view_mocks(self, mocker):
        """Setup mocks for all view tests"""
        # Create the mock with the methods we want to use
        mock_instance = mocker.Mock()
        mock_instance.has_permission = mocker.Mock(return_value=False)
        mock_instance.has_person = mocker.Mock(return_value=False)
        
        # Create the service mock that returns our instance
        self.mock_service = mocker.patch(
            'apps.product_management.flows.challenge_authoring.views.ChallengeAuthoringService',
            return_value=mock_instance
        )
        return self.mock_service

    @pytest.fixture(autouse=True)
    def setup(self, setup_product_manager, mock_template):
        """Ensure product manager role is set up"""
        self.mock_template = mock_template

    def test_view_requires_authentication(self, client, product):
        """Test that unauthenticated users cannot access the view"""
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_view_requires_person(self, client, user, product, mock_role_service):
        """Test that users without person object cannot access the view"""
        user.person = None
        user.save()
        mock_role_service.return_value.is_product_manager.return_value = False
        client.force_login(user)
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        response = client.get(url)
        assert response.status_code == 403

    def test_view_requires_product_manager(self, client, user, product, mock_role_service):
        """Test that non-managers cannot access the view"""
        mock_role_service.return_value.is_product_manager.return_value = False
        client.force_login(user)
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        response = client.get(url)
        assert response.status_code == 403

    def test_successful_challenge_creation(
        self, client, user, product, mock_service, valid_challenge_data, mocker
    ):
        """Test successful challenge creation flow"""
        client.force_login(user)
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        
        mock_challenge = mocker.Mock()
        mock_challenge.get_absolute_url.return_value = '/test/url'
        mock_service.create_challenge.return_value = (True, mock_challenge, None)
        
        response = client.post(
            url,
            data=json.dumps(valid_challenge_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.json() == {'redirect_url': '/test/url'}

    def test_bounty_modal_api_endpoints(self, client, user, product, mock_role_service, mocker):
        """Test the API endpoints used by BountyModal.js"""
        client.force_login(user)
        url = reverse('bounty_modal', kwargs={'product_slug': product.slug})
        
        mock_service_class = mocker.patch('apps.product_management.flows.challenge_authoring.views.ChallengeAuthoringService')
        instance = mock_service_class.return_value
        instance.get_skills_list.return_value = []
        instance.is_product_manager.return_value = True
        response = client.get(url)
        assert response.status_code == 200

    def test_permission_checks(self, client, user, product, mock_role_service):
        """Test permission requirements"""
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        
        # Test unauthenticated
        response = client.get(url)
        assert response.status_code == 302  # Redirects to login
        
        # Test authenticated but not product manager
        mock_role_service.return_value.is_product_manager.return_value = False
        client.force_login(user)
        response = client.get(url)
        assert response.status_code == 403

    def test_form_validation(self, client, user, product, mock_service, mock_role_service):
        mock_role_service.is_product_manager.return_value = True  # Ensure permission check passes
        client.force_login(user)
        url = reverse('challenge_create', kwargs={'product_slug': product.slug})
        
        mock_service.create_challenge.return_value = (False, None, {'title': ['This field is required']})
        
        response = client.post(
            url,
            data=json.dumps({
                'title': '',
                'description': '',
                'bounties': []
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert 'errors' in response.json()

    def test_skills_api(self, client, user, product, mock_role_service):
        """Test skills list and expertise endpoints"""
        client.force_login(user)
        
        # Test skills list
        url = reverse('challenge_skills', kwargs={'product_slug': product.slug})
        response = client.get(url)
        assert response.status_code == 200

    def test_expertise_list(self, client, user, product, expertise_items):
        """Test expertise list retrieval"""
        client.force_login(user)
        skill = expertise_items[0].skill
        url = reverse('skill_expertise', kwargs={
            'product_slug': product.slug,
            'skill_id': skill.id
        })
        
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert 'expertise' in data
        expertise_list = data['expertise']
        assert len(expertise_list) == 2
        names = sorted(e['name'] for e in expertise_list)
        assert names == ["React", "React Advanced"]

class TestChallengeAuthoringService:
    @pytest.fixture(autouse=True)
    def setup_service_mocks(self, mocker):
        """Setup common service mocks"""
        # Mock RoleService in the services module
        self.mock_role_service = mocker.patch(
            'apps.product_management.flows.challenge_authoring.services.RoleService',
            autospec=True
        )
        # Create and configure mock instance
        self.mock_instance = mocker.Mock()
        self.mock_role_service.return_value = self.mock_instance
        self.mock_instance.is_product_manager.return_value = True
        return self.mock_role_service

    def test_service_initialization(self, user, product, mocker):
        """Test service initialization with permissions"""
        mock_role_service = mocker.patch(
            'apps.product_management.flows.challenge_authoring.services.RoleService'
        )
        mock_instance = mock_role_service.return_value
        mock_instance.is_product_manager.return_value = True
        
        service = ChallengeAuthoringService(user, product.slug)
        
        mock_instance.is_product_manager.assert_called_once_with(
            user.person,
            product
        )

    def test_service_initialization_permission_denied(self, user, product):
        """Test service initialization without permissions"""
        # Configure the mock to deny permission
        self.mock_instance.is_product_manager.return_value = False
        
        with pytest.raises(PermissionDenied) as exc_info:
            ChallengeAuthoringService(user, product.slug)
            
        assert "Must be product manager" in str(exc_info.value)
        
        # Verify the mock was called with correct arguments
        assert self.mock_instance.is_product_manager.call_count == 1
        self.mock_instance.is_product_manager.assert_called_with(
            user.person,
            product
        )

    @pytest.mark.django_db
    def test_challenge_creation(self, user, product, valid_challenge_data, valid_bounties_data, skills):
        """Test full challenge creation flow"""
        service = ChallengeAuthoringService(user, product.slug)
        
        # Update bounties data to use expertise.set() instead of direct assignment
        valid_bounties_data[0].update({
            'skill': skills[0],
            'expertise_ids': [e.id for e in Expertise.objects.filter(skill=skills[0])]
        })
        
        with transaction.atomic():
            success, challenge, errors = service.create_challenge(
                valid_challenge_data,
                valid_bounties_data
            )
        
        assert success is True
        assert challenge is not None
        assert errors is None

    def test_validation_errors(self, user, product):
        """Test validation error handling"""
        service = ChallengeAuthoringService(user, product.slug)
        
        invalid_data = {
            'title': '',  # Empty title
            'description': '',  # Empty description
            'status': 'invalid',  # Invalid choice
        }
        
        success, challenge, errors = service.create_challenge(invalid_data, [])
        
        assert success is False
        assert 'title' in errors
        assert 'description' in errors
        assert 'status' in errors

    def test_bounty_validation(self, user, product, valid_challenge_data, invalid_bounties_data, mock_role_service):
        """Test bounty validation rules"""
        service = ChallengeAuthoringService(user, product.slug)
        
        success, challenge, errors = service.create_challenge(
            valid_challenge_data,
            invalid_bounties_data
        )
        
        assert success is False
        assert challenge is None
        assert errors is not None
        assert 'bounties' in errors
        assert 'points' in str(errors['bounties'][0])  # Points validation error
        assert 'title' in str(errors['bounties'][0])   # Title validation error
        assert 'points' in str(errors['bounties'][1])  # Max points exceeded

    @pytest.mark.django_db
    def test_transaction_rollback(self, user, product, valid_challenge_data):
        service = ChallengeAuthoringService(user, product.slug)

        invalid_bounties = [{
            'title': 'Test Bounty',
            'description': 'Test Description',
            'points': 100,
            'skill_id': 999,  # Invalid skill ID
            'expertise_ids': [1]
        }]

        success, challenge, errors = service.create_challenge(
            valid_challenge_data,
            invalid_bounties
        )

        assert success is False
        assert challenge is None
        assert errors['bounties'][0].startswith('Invalid skill ID')

    @pytest.mark.django_db
    def test_max_bounties_limit(self, user, product, valid_challenge_data, skills, mock_role_service):
        """Test maximum number of bounties per challenge"""
        service = ChallengeAuthoringService(user, product.slug)
        
        too_many_bounties = [
            {
                'title': f'Bounty {i}',
                'description': 'Test bounty description',
                'points': 100,
                'skill_id': skills[0].id,
                'expertise': [1]
            }
            for i in range(11)
        ]
        
        success, challenge, errors = service.create_challenge(
            valid_challenge_data,
            too_many_bounties
        )
        
        assert success is False
        assert 'bounties' in errors

    @pytest.mark.django_db
    def test_total_points_limit(self, user, product, valid_challenge_data, mock_role_service):
        service = ChallengeAuthoringService(user, product.slug)
        
        high_point_bounties = [
            {
                'title': f'Bounty {i}',
                'description': 'Test bounty description',
                'points': 100,
                'skill_id': 1,
                'expertise_ids': [1]
            }
            for i in range(11)  # 1100 points total
        ]
        
        success, challenge, errors = service.create_challenge(
            valid_challenge_data,
            high_point_bounties
        )
        
        assert success is False
        assert challenge is None
        assert errors is not None
        assert 'bounties' in errors
        assert any('total points' in error.lower() for error in errors['bounties'])

    def test_get_skills_list(self, user, product, skills):
        """Test skills list retrieval"""
        service = ChallengeAuthoringService(user, product.slug)
        skills_list = service.get_skills_list()
        
        assert len(skills_list) == 2
        skill_names = {skill['name'] for skill in skills_list}
        assert 'Frontend Development' in skill_names
        assert 'Backend Development' in skill_names

    def test_get_expertise_for_skill(self, user, product, expertise_items):
        service = ChallengeAuthoringService(user, product.slug)
        skill_id = expertise_items[0].skill.id
        expertise_list = service.get_expertise_for_skill(skill_id)
        
        assert len(expertise_list) == 2
        assert all(e['name'] in ['React', 'React Advanced'] for e in expertise_list)

    def test_expertise_ids_format(self, user, product, valid_challenge_data, expertise_items):
        service = ChallengeAuthoringService(user, product.slug)
        
        bounties_data = [{
            'title': 'Test Bounty',
            'description': 'Test Description',
            'points': 100,
            'skill_id': expertise_items[0].skill.id,
            'expertise_ids': [e.id for e in expertise_items]
        }]
        
        success, _, _ = service.create_challenge(
            valid_challenge_data,
            bounties_data
        )
        assert success is True

    def test_validation_rules(self, user, product):
        """Test all validation rules for challenges and bounties"""
        service = ChallengeAuthoringService(user, product.slug)
        
        # Test challenge validation
        invalid_challenge = {
            'title': 'A' * 256,  # Exceeds MAX_TITLE_LENGTH
            'description': 'Too short',  # Less than 50 chars
            'status': 'INVALID_STATUS',
            'priority': 'INVALID_PRIORITY',
            'video_url': 'not-a-url'
        }
        
        errors = service._validate_challenge(invalid_challenge)
        assert len(errors) > 0
        assert any('Title must be less than' in error for error in errors)
        assert any('Description must be at least' in error for error in errors)
        assert any('Invalid status' in error for error in errors)
        assert any('Invalid priority' in error for error in errors)
        assert any('Invalid video URL format' in error for error in errors)

    def test_bounty_validation(self, user, product):
        """Test bounty-specific validation rules"""
        service = ChallengeAuthoringService(user, product.slug)
        
        invalid_bounties = [
            {
                'title': '',
                'description': '',
                'points': 0,
                'skill': None,
                'expertise_ids': []
            }
        ] * 11  # Exceeds MAX_BOUNTIES
        
        errors = service._validate_bounties(invalid_bounties)
        assert any(f'Maximum of {service.MAX_BOUNTIES} bounties' in error for error in errors)

    def test_expertise_validation(self, user, product, mock_expertise):
        """Test expertise validation for bounties"""
        service = ChallengeAuthoringService(user, product.slug)
        
        bounty_data = [{
            'title': 'Test Bounty',
            'description': 'Description',
            'points': 100,
            'skill': 1,
            'expertise_ids': '999'  # Non-existent expertise
        }]
        
        errors = service._validate_bounties(bounty_data)
        assert any('Invalid expertise selection' in error for error in errors)

    def test_cross_validation(self, user, product):
        """Test validation between challenges and bounties"""
        service = ChallengeAuthoringService(user, product.slug)
        
        challenge_data = {
            'status': 'ACTIVE',
            'reward_type': 'POINTS'
        }
        bounties_data = []  # Empty bounties for active challenge
        
        errors = service._validate_challenge_bounty_relationship(
            challenge_data,
            bounties_data
        )
        assert any('Active challenges must have at least one bounty' in error for error in errors)

    def test_get_skills_tree(self, user, product, mock_role_service):
        """Test hierarchical skills retrieval"""
        service = ChallengeAuthoringService(user, product.slug)
        
        # Create test data with unique names
        parent_skill = Skill.objects.create(
            name="Web Development Test",
            selectable=True
        )
        child_skill = Skill.objects.create(
            name="Frontend Development Test",
            parent=parent_skill,
            selectable=True
        )

class TestSkillEndpoints:
    """Test cases for skill and expertise API endpoints"""
    
    def test_skills_list_requires_auth(self, client, product):
        """Test that unauthenticated users cannot access skills list"""
        url = reverse('challenge_skills', kwargs={'product_slug': product.slug})
        response = client.get(url)
        assert response.status_code == 302  # Redirects to login

    def test_skills_list(self, client, user, product):
        """Test successful skills list retrieval"""
        client.force_login(user)
        url = reverse('challenge_skills', kwargs={'product_slug': product.slug})
        response = client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert 'skills' in data
        assert len(data['skills']) == 2
        assert data['skills'][0]['name'] == 'Frontend Development'

    def test_expertise_requires_auth(self, client, product, skills):
        """Test that unauthenticated users cannot access expertise list"""
        url = reverse('skill_expertise', kwargs={
            'product_slug': product.slug,
            'skill_id': skills[0].id
        })
        response = client.get(url)
        assert response.status_code == 302  # Redirects to login

    def test_expertise_list(self, client, user, product, expertise_items, skills):
        """Test expertise list retrieval"""
        client.force_login(user)
        skill = skills[0]  # Frontend Development skill
        url = reverse('skill_expertise', kwargs={
            'product_slug': product.slug,
            'skill_id': skill.id
        })
        
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert 'expertise' in data
        expertise_list = data['expertise']
        assert len(expertise_list) == 2
        names = sorted(e['name'] for e in expertise_list)
        assert names == ["React", "React Advanced"]

    def test_expertise_invalid_skill(self, client, user, product):
        """Test expertise retrieval with invalid skill ID"""
        client.force_login(user)
        url = reverse('skill_expertise', kwargs={
            'product_slug': product.slug,
            'skill_id': 99999  # Non-existent ID
        })
        response = client.get(url)
        assert response.status_code == 404
