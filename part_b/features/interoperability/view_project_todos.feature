
Feature: View Project Todos
  As a user
  I want to view the todos belonging to a project
  So that I can track the tasks associated with it

  Background:
    Given the Interoperability API is running

  # Normal Flow
  Scenario Outline: View a project with one linked todo
    Given a project named "<project_title>" exists
    And a todo named "<todo_title>" exists
    And the todo is linked to the project
    When I request the todos belonging to the project
    Then the interoperability response status should be 200
    And the project todo list should contain the linked todo

    Examples:
      | project_title | todo_title       |
      | ECSE 429      | Write test cases |
      | Website       | Design homepage  |

  # Alternate Flow
  Scenario Outline: View a project with two linked todos
    Given a project named "<project_title>" exists
    And a todo named "<first_todo>" exists
    And another todo named "<second_todo>" exists
    And both todos are linked to the project
    When I request the todos belonging to the project
    Then the interoperability response status should be 200
    And the project todo list should contain both linked todos

    Examples:
      | project_title | first_todo     | second_todo     |
      | Final Report  | Write report   | Review report   |
      | Sprint Tasks  | Implement API  | Test API        |

 # Error Flow
Scenario Outline: Reject an unsupported response format for project todos
  Given a project named "<project_title>" exists
  When I request the project todos with unsupported Accept "<media_type>"
  Then the interoperability response status should be 406

  Examples:
    | project_title | media_type       |
    | Coursework    | text/plain       |
    | Sprint Tasks  | application/yaml |