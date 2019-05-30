function showBox(){
    var show = "";
    var listOfInputs = document.getElementsByName("answer");

    for (var i = 0; i<listOfInputs.length; i++ )
    {
        if(listOfInputs[i].checked){
            show = listOfInputs[i].value;
        }
    }

    if(show=="1"){
        document.getElementById("idAndName").style.display="none";
    }
    else{
        document.getElementById("idAndName").style.display="block";
    }
}