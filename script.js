async function predictCategory(){

    const description =
        document.getElementById("projectDescription").value;

    if(description===""){

        alert("Please enter your project description.");

        return;

    }

    document.getElementById("result").innerHTML="Predicting...";

    try{

        const response=await fetch("/project",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                description:description

            })

        });

        const data=await response.json();

        document.getElementById("result").innerHTML=

        "<h2>Predicted Category</h2><br>"+data.prediction;

    }

    catch(error){

        document.getElementById("result").innerHTML=

        "Something went wrong.";

    }

}