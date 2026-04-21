import {configureStore} from "@reduxjs/toolkit";
import counterReducer from "./slices/counterSlice";
import authReducer from "./slices/authSlice";
import cartReducer from "./slices/cartSlice";
import userReducer from "./slices/userSlice";


const store = configureStore({
    reducer :{
        counter:counterReducer,
        auth:authReducer,
        cart:cartReducer,
        user:userReducer
    }
});
export default store;
