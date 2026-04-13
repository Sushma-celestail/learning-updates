const Button = ({ label, color, onClick }) => {
  return (
    <button
      onClick={onClick}
      style={{ backgroundColor: color, color: "#fff", margin: 5 }}
    >
      {label}
    </button>
  );
};

export default Button;