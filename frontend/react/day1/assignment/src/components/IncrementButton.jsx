import React from "react";

const IncrementButton = React.memo(({ onIncrement }) => {
  console.log("Increment Button Rendered");

  return <button onClick={onIncrement}>Increment</button>;
});

export default IncrementButton;