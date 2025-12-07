import pytest
import sys
import os

# Add app directory to path if main.py is in app/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# If main.py is in root, use this instead:
# from main import app, tasks

# If main.py is in app/ folder, use this:
try:
    from main import app, tasks
except ImportError:
    from app.main import app, tasks


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_tasks():
    """Clear tasks before and after each test"""
    tasks.clear()
    yield
    tasks.clear()


class TestHomePage:
    """Tests for the home page"""
    
    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Task Manager' in response.data
    
    def test_empty_task_list(self, client):
        """Test home page with no tasks"""
        response = client.get('/')
        assert b'No tasks yet' in response.data or b'task-card' not in response.data


class TestAddTask:
    """Tests for adding tasks"""
    
    def test_add_task_success(self, client):
        """Test adding a valid task"""
        response = client.post('/add', data={
            'task': 'Test Task',
            'priority': '2',
            'category': 'General'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Test Task' in response.data
    
    def test_add_task_with_high_priority(self, client):
        """Test adding a high priority task"""
        response = client.post('/add', data={
            'task': 'Urgent Task',
            'priority': '3',
            'category': 'Work'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert len(tasks) == 1
        assert tasks[0]['priority'] == 3
    
    def test_add_empty_task(self, client):
        """Test that empty tasks are rejected"""
        response = client.post('/add', data={
            'task': '',
            'priority': '2',
            'category': 'General'
        }, follow_redirects=True)
        
        assert len(tasks) == 0
    
    def test_add_multiple_tasks(self, client):
        """Test adding multiple tasks"""
        client.post('/add', data={'task': 'Task 1', 'priority': '2', 'category': 'General'})
        client.post('/add', data={'task': 'Task 2', 'priority': '1', 'category': 'Personal'})
        client.post('/add', data={'task': 'Task 3', 'priority': '3', 'category': 'Work'})
        
        assert len(tasks) == 3


class TestCompleteTask:
    """Tests for completing tasks"""
    
    def test_complete_task(self, client):
        """Test marking a task as complete"""
        # Add a task first
        client.post('/add', data={'task': 'Complete Me', 'priority': '2', 'category': 'General'})
        task_id = tasks[0]['id']
        
        # Mark it complete
        response = client.get(f'/complete/{task_id}', follow_redirects=True)
        assert response.status_code == 200
        assert tasks[0]['completed'] == True
    
    def test_toggle_complete(self, client):
        """Test toggling task completion status"""
        client.post('/add', data={'task': 'Toggle Me', 'priority': '2', 'category': 'General'})
        task_id = tasks[0]['id']
        
        # Complete it
        client.get(f'/complete/{task_id}')
        assert tasks[0]['completed'] == True
        
        # Uncomplete it
        client.get(f'/complete/{task_id}')
        assert tasks[0]['completed'] == False


class TestDeleteTask:
    """Tests for deleting tasks"""
    
    def test_delete_task(self, client):
        """Test deleting a task"""
        client.post('/add', data={'task': 'Delete Me', 'priority': '2', 'category': 'General'})
        task_id = tasks[0]['id']
        
        response = client.get(f'/delete/{task_id}', follow_redirects=True)
        assert response.status_code == 200
        assert len(tasks) == 0
    
    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist"""
        response = client.get('/delete/999', follow_redirects=True)
        assert response.status_code == 200  # Should not crash


class TestEditTask:
    """Tests for editing tasks"""
    
    def test_edit_task(self, client):
        """Test editing a task"""
        client.post('/add', data={'task': 'Original Task', 'priority': '2', 'category': 'General'})
        task_id = tasks[0]['id']
        
        response = client.post(f'/edit/{task_id}', data={
            'new_title': 'Updated Task',
            'new_priority': '3',
            'new_category': 'Work'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert tasks[0]['title'] == 'Updated Task'
        assert tasks[0]['priority'] == 3
        assert tasks[0]['category'] == 'Work'
    
    def test_edit_with_empty_title(self, client):
        """Test editing with empty title should keep original"""
        client.post('/add', data={'task': 'Original', 'priority': '2', 'category': 'General'})
        task_id = tasks[0]['id']
        
        client.post(f'/edit/{task_id}', data={
            'new_title': '',
            'new_priority': '3',
            'new_category': 'Work'
        })
        
        assert tasks[0]['title'] == 'Original'  # Title unchanged


class TestClearCompleted:
    """Tests for clearing completed tasks"""
    
    def test_clear_completed_tasks(self, client):
        """Test clearing all completed tasks"""
        # Add 3 tasks
        client.post('/add', data={'task': 'Task 1', 'priority': '2', 'category': 'General'})
        client.post('/add', data={'task': 'Task 2', 'priority': '2', 'category': 'General'})
        client.post('/add', data={'task': 'Task 3', 'priority': '2', 'category': 'General'})
        
        # Complete 2 of them
        client.get(f'/complete/{tasks[0]["id"]}')
        client.get(f'/complete/{tasks[1]["id"]}')
        
        # Clear completed
        response = client.post('/clear_completed', follow_redirects=True)
        
        assert response.status_code == 200
        assert len(tasks) == 1  # Only 1 incomplete task remains
        assert tasks[0]['title'] == 'Task 3'


class TestStats:
    """Tests for statistics endpoint"""
    
    def test_stats_empty(self, client):
        """Test stats with no tasks"""
        response = client.get('/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['total'] == 0
        assert data['completed'] == 0
        assert data['pending'] == 0
    
    def test_stats_with_tasks(self, client):
        """Test stats with mixed tasks"""
        client.post('/add', data={'task': 'Task 1', 'priority': '2', 'category': 'General'})
        client.post('/add', data={'task': 'Task 2', 'priority': '2', 'category': 'General'})
        client.post('/add', data={'task': 'Task 3', 'priority': '2', 'category': 'General'})
        
        # Complete one
        client.get(f'/complete/{tasks[0]["id"]}')
        
        response = client.get('/stats')
        data = response.get_json()
        
        assert data['total'] == 3
        assert data['completed'] == 1
        assert data['pending'] == 2


class TestTaskSorting:
    """Tests for task sorting functionality"""
    
    def test_tasks_sorted_by_priority(self, client):
        """Test that tasks are sorted by priority"""
        client.post('/add', data={'task': 'Low', 'priority': '1', 'category': 'General'})
        client.post('/add', data={'task': 'High', 'priority': '3', 'category': 'General'})
        client.post('/add', data={'task': 'Medium', 'priority': '2', 'category': 'General'})
        
        response = client.get('/')
        # High priority tasks should appear first in the HTML
        assert response.data.index(b'High') < response.data.index(b'Medium')
        assert response.data.index(b'Medium') < response.data.index(b'Low')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])