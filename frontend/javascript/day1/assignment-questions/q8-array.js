// Section C — Arrays & Array Methods

// Q8. Array Pipeline — Student Grade Processor

// Topics: map, filter, reduce, sort, Method Chaining


// Problem Statement:

// Given an array of student objects, write a processing pipeline using method chaining (no intermediate variables).


// Input:

// const students = [

// { name: "Alice", scores: [85, 92, 78] },

// { name: "Bob", scores: [45, 55, 60] },

// { name: "Carol", scores: [90, 95, 88] },

// { name: "Dave", scores: [30, 40, 35] },

// { name: "Eve", scores: [72, 68, 75] },

// ];


// Output:

// [

// { name: "Carol", average: 91, grade: "A" },

// { name: "Alice", average: 85, grade: "B" },

// { name: "Eve", average: 71.67, grade: "C" }

// ]


// Constraints:

// • Step 1: map to compute average (rounded to 2 decimal places)

// • Step 2: filter to include only average >= 60

// • Step 3: sort by average descending

// • Step 4: map to assign grade: A (>=90), B (>=80), C (>=70), D (>=60)

// • Must be a single chained expression

// • Do NOT use for/while loops


const students = [
    { name: "Alice", scores: [85, 92, 78] },
    { name: "Bob", scores: [45, 55, 60] },
    { name: "Carol", scores: [90, 95, 88] },
    { name: "Dave", scores: [30, 40, 35] },
    { name: "Eve", scores: [72, 68, 75] },
];

const result = students
    // Step 1: Compute average
    .map(student => {
        const avg =
            student.scores.reduce((sum, s) => sum + s, 0) /
            student.scores.length;

        return {
            name: student.name,
            average: Number(avg.toFixed(2)) // round to 2 decimals
        };
    })

    // Step 2: Filter average >= 60
    .filter(student => student.average >= 60)

    // Step 3: Sort descending
    .sort((a, b) => b.average - a.average)

    // Step 4: Assign grade
    .map(student => {
        let grade;

        if (student.average >= 90) grade = "A";
        else if (student.average >= 80) grade = "B";
        else if (student.average >= 70) grade = "C";
        else grade = "D";

        return {
            ...student,
            grade
        };
    });

console.log(result);
