
Feature: Link Todo to Category
  As a user
  I want to assign categories to my todos
  So that I can organize related tasks

  Background:
    Given the Interoperability API is running

  # Normal Flow
  Scenario Outline: Link a category to an existing todo
    Given a todo named "<todo_title>" exists
    And a category named "<category_title>" exists
    When I link the category to the todo
    Then the interoperability response status should be 201
    And the todo should contain the linked category

    Examples:
      | todo_title      | category_title |
      | Finish homework | School         |
      | Buy groceries   | Personal       |

  # Alternate Flow
  Scenario Outline: Link two categories to one todo
    Given a todo named "<todo_title>" exists
    And a category named "<first_category>" exists
    And another category named "<second_category>" exists
    When I link both categories to the todo
    Then the interoperability response status should be 201
    And the todo should contain both linked categories

    Examples:
      | todo_title    | first_category | second_category |
      | Read textbook | School         | Reading         |
      | Plan vacation | Personal       | Travel          |

  # Error Flow
  Scenario Outline: Reject linking a nonexistent category
    Given a todo named "<todo_title>" exists
    When I try to link a category with invalid ID "<invalid_id>"
    Then the interoperability response status should be 404
    And the todo should have no linked categories

    Examples:
      | todo_title    | invalid_id |
      | Review notes  | abc        |
      | Submit report | missing    |
