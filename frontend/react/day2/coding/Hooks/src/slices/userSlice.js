import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Async thunk
export const fetchUsers = createAsyncThunk(
  "user/fetchUsers",
  async () => {
    const response = await fetch("https://jsonplaceholder.typicode.com/users");
    return response.json();
  }
);

const userSlice = createSlice({
  name: "user",
  initialState: {
    users: [],
    status: "idle"
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state) => {
        state.status = "failed";
      });
  }
});

export default userSlice.reducer;