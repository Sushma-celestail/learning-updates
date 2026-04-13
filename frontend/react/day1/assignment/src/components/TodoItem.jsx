import React from "react";

const TodoItem = React.memo(({ todo, onDelete }) => {
  console.log("Rendering:", todo);

  return (
    <li>
      {todo}
      <button onClick={() => onDelete(todo)}>Delete</button>
    </li>
  );
});

export default TodoItem;