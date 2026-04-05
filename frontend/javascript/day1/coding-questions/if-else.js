function getStatusCategory(status){
    if (status >= 200 && status < 300){
        return "success";
    }else if (status >= 300 && status < 400){
        return "redirect"
    }else if (status >= 400 && status < 500){
        return "client_error"
    }else if (status >= 500 && status < 600){
        return "server_error";
    }else{
        return "unknown";
    }
}

console.log(getStatusCategory(400))

console.log(getStatusCategory(550))



function getStatusCategorySwitch(status) {
    switch (true) {
        case (status >= 200 && status < 300):
            return "success";
        case (status >= 300 && status < 400):
            return "redirect";
        case (status >= 400 && status < 500):
            return "client_error";
        case (status >= 500 && status < 600):
            return "server_error";
        default:
            return "unknown";
    }
}


console.log(getStatusCategory(400))