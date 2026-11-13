
Feature: Unlink Todo from Project
  As a user
  I want to remove a todo from a project
  So that I can reorganize tasks without deleting them

  Background:
    Given the Interoperability API is running

  # Normal Flow
  Scenario Outline: Unlink an existing todo from a project
    Given a project named "<project_title>" exists
    And a todo named "<todo_title>" exists
    And the todo is linked to the project
    When I unlink the todo from the project
    Then the interoperability response status should be 200
    And the project should have no linked todos
    And the todo and project should still exist

    Examples:
      | project_title | todo_title       |
      | Coursework    | Finish homework  |
      | Website       | Design homepage  |

  # Alternate Flow
  Scenario Outline: Unlink one todo while preserving another
    Given a project named "<project_title>" exists
    And a todo named "<first_todo>" exists
    And another todo named "<second_todo>" exists
    And both todos are linked to the project
    When I unlink the first todo from the project
    Then the interoperability response status should be 200
    And the project should contain only the second todo
    And both todos should still exist

    Examples:
      | project_title | first_todo    | second_todo    |
      | Final Report  | Write report  | Review report  |
      | Sprint Tasks  | Implement API | Test API       |

  # Error Flow
  Scenario Outline: Reject unlinking a todo that is not linked
    Given a project named "<project_title>" exists
    And a todo named "<todo_title>" exists
    When I unlink the todo from the project
    Then the interoperability response status should be 404
    And the project should have no linked todos
    And the todo and project should still exist

    Examples:
      | project_title | todo_title     |
      | Research      | Read papers    |
      | Sprint Review | Prepare slides |
