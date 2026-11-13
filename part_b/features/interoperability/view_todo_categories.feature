
Feature: View Todo Categories
  As a user
  I want to view the categories assigned to a todo
  So that I can understand how my tasks are organized

  Background:
    Given the Interoperability API is running

  # Normal Flow
  Scenario Outline: View a todo with one linked category
    Given a todo named "<todo_title>" exists
    And a category named "<category_title>" exists
    And the category is linked to the todo
    When I request the categories belonging to the todo
    Then the interoperability response status should be 200
    And the todo category list should contain the linked category

    Examples:
      | todo_title       | category_title |
      | Finish homework  | School         |
      | Buy groceries    | Personal       |

  # Alternate Flow
  Scenario Outline: View a todo with two linked categories
    Given a todo named "<todo_title>" exists
    And a category named "<first_category>" exists
    And another category named "<second_category>" exists
    And both categories are linked to the todo
    When I request the categories belonging to the todo
    Then the interoperability response status should be 200
    And the todo category list should contain both linked categories

    Examples:
      | todo_title      | first_category | second_category |
      | Read textbook   | School         | Reading         |
      | Plan vacation   | Personal       | Travel          |

  # Error Flow
  Scenario Outline: Reject an unsupported response format for todo categories
    Given a todo named "<todo_title>" exists
    When I request the todo categories with unsupported Accept "<media_type>"
    Then the interoperability response status should be 406

    Examples:
      | todo_title     | media_type       |
      | Review notes   | text/plain       |
      | Submit report  | application/yaml |
