// Aggiungi un gestore di eventi al pulsante "Predict"
const predictButton = document.getElementById("submitBtn");
predictButton.addEventListener("click", getPrediction);

// Ottenere i riferimenti agli elementi HTML
diabetesBinaryElement = document.getElementById("diabetesBinary");
predictionElement = document.getElementById("prediction");
probability0Element = document.getElementById("probability0");
probability1Element = document.getElementById("probability1");


function getPrediction() {
    const jsonReq = getJson();
    console.log(jsonReq);
    sendRequest(jsonReq);
}

function getJson() {
    const data = {
        diabetes_binary: document.getElementById("DiabetResponse_opt").value,
        highbp: document.getElementById("HighBP_opt").value,
        highchol: document.getElementById("HighChol_opt").value,
        cholcheck: document.getElementById("CholCheck_opt").value,
        bmi: document.getElementById("BMI_opt").value,
        smoker: document.getElementById("Smoking_opt").value,
        stroke: document.getElementById("Stroke_opt").value,
        heartdiseaseorattack: document.getElementById("HearthDisease_opt").value,
        physactivity: document.getElementById("PhysicalActivity_opt").value,
        fruits: document.getElementById("Fruits_opt").value,
        veggies: document.getElementById("Veggies_opt").value,
        hvyalcoholconsump: document.getElementById("AlcoholDrinking_opt").value,
        anyhealthcare: document.getElementById("AnyHealthCare_opt").value,
        genhlth: document.getElementById("GenHealth_opt").value,
        menthlth: document.getElementById("MentalHealth_opt").value,
        physhlth: document.getElementById("PhysicalHealt_opt").value,
        diffwalk: document.getElementById("DiffWalking_opt").value,
        sex: document.getElementById("Sex_opt").value,
        age: document.getElementById("AgeCategory_opt").value,
        education: document.getElementById("Education_opt").value,
        income: document.getElementById("Income_opt").value
    };

    const postData = {
        id: "input",
        arguments: data
    };

    return postData;
}

function sendRequest(jsonReq) {
    const xhr = new XMLHttpRequest();
    const url = "http://localhost:8080/openscoring/model/Diabetes";

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('Accept', 'application/json');

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                const response = JSON.parse(xhr.responseText);

                
                // Estrarre i valori dei risultati dalla risposta
                 
                 predictionValue = response.results.prediction;
                 probability0Value = response.results["probability(0)"];
                 probability1Value = response.results["probability(1)"];

                // Inserire i valori nei rispettivi elementi HTML
                diabetesBinaryElement.innerText = document.getElementById("DiabetResponse_opt").value;
                predictionElement.innerText = predictionValue;
                probability0Element.innerText = probability0Value;
                probability1Element.innerText = probability1Value;
            } else {
                console.log("Errore durante la richiesta: " + xhr.status);
            }
        }
    };

    const data = JSON.stringify(jsonReq);
    xhr.send(data);
}





function registerResponse() {
    const currentdate = new Date();
    let date_id = "" + currentdate.getFullYear() + (currentdate.getMonth() + 1) + currentdate.getDate() + currentdate.getHours() + currentdate.getMinutes() + currentdate.getSeconds();
    
    if (location.hostname != "") {
        date_id += location.hostname;
    }
    
    const json = {
        id: String(date_id),
        diabets_binary: Number(document.getElementById("DiabetResponse_opt").value),
        highbp: Number(document.getElementById("HighBP_opt").value),
        highchol: Number(document.getElementById("HighChol_opt").value),
        cholcheck: Number(document.getElementById("CholCheck_opt").value),
        bmi: Number(document.getElementById("BMI_opt").value),
        smoker: Number(document.getElementById("Smoking_opt").value),
        stroke: Number(document.getElementById("Stroke_opt").value),
        heartdiseaseorattack: Number(document.getElementById("HearthDisease_opt").value),
        physactivity: Number(document.getElementById("PhysicalActivity_opt").value),
        fruits: Number(document.getElementById("Fruits_opt").value),
        veggies: Number(document.getElementById("Veggies_opt").value),
        hvyalcoholconsump: Number(document.getElementById("AlcoholDrinking_opt").value),
        anyhealthcare: Number(document.getElementById("AnyHealthCare_opt").value),
        nodocbccost: Number("0.0"),
        genhlth: Number(document.getElementById("GenHealth_opt").value),
        menthlth: Number(document.getElementById("MentalHealth_opt").value),
        physhlth: Number(document.getElementById("PhysicalHealt_opt").value),
        diffwalk: Number(document.getElementById("DiffWalking_opt").value),
        sex: Number(document.getElementById("Sex_opt").value),
        age: Number(document.getElementById("AgeCategory_opt").value),
        education: Number(document.getElementById("Education_opt").value),
        income: Number(document.getElementById("Income_opt").value)
    };
    
    const postData = {
        id: "input",
        arguments: json
    };
    
    const xhr = new XMLHttpRequest();
    const url = "http://127.0.0.1:5002/insert";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader('Accept', 'application/json');
    console.log(postData)
    
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const response = JSON.parse(xhr.responseText);
            // Esegui le azioni desiderate con la risposta
            console.log("Funzionante");
            //alert("Utente registrato correttamente nel database");
            resetAll();

        }else {
      console.error("Errore nella richiesta:", xhr.status, xhr.statusText);
      console.error("Dettagli errore:", xhr.responseText);
    }
        
    };
    
    const data = JSON.stringify(postData);
    xhr.send(data);
}
