function sayHi(){
    if (true){
        // var name="hello"
        // console.log(name);
        // let a=2;
        // let b=4;
        // console.log(a+b);
        // alert(b)
        // alert(a)
        // alert(a+b);
        let counter=2;
        counter++;
        console.log(counter);

        console.log(9007199254740991+1);
        console.log(9007199254740991+2);
        const bigInt = 1234567890123456789012345678901234567890n;
        console.log(bigInt);
        console.log(bigInt + 1n);
        console.log(typeof bigInt);
        console.log(typeof "foo");
        console.log(typeof Symbol("id"));
        let age = prompt('How old are you?', 100);

        alert(`You are ${age} years old!`); 
    }}
sayHi()