import React from "react";
import { useForm } from "react-hook-form";

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitSuccessful }
  } = useForm();

  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      
      {/* Email Field */}
      <input
        placeholder="Enter Email"
        {...register("email", {
          required: "Email is required",
          pattern: {
            value: /\S+@\S+\.\S+/,
            message: "Enter a valid email"
          }
        })}
      />
      {errors.email && <p className="error">{errors.email.message}</p>}

      {/* Password Field */}
      <input
        type="password"
        placeholder="Enter Password"
        {...register("password", {
          required: "Password is required",
          minLength: {
            value: 6,
            message: "Min 6 characters"
          }
        })}
      />
      {errors.password && <p className="error">{errors.password.message}</p>}

      <button type="submit">Login</button>

      {isSubmitSuccessful && <p>✅ Login successful</p>}
    </form>
  );
}

export default LoginForm;