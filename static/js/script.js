// tanaka

jQuery(function($){

    // tanaka ajax
    // $('#plus').click(function(){

        // var session_id = $('#session_id').val();
        // $.ajax({
        //     url: "/home/game",
        //     type: 'post',
        //     contentType:'application/json',
        //     data : JSON.stringify({"action" : 'plus'}),
        // }).done(function(data) {
        //     console.log(data);
        // }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
        //     console.log(textStatus)
        // })
    // }); 

    // $('#submit').click(function(){
    //     var session_id = $('#session_id').val();
    //     $.ajax({
    //         url: "/home/game",
    //         type: 'post',
    //         contentType:'application/json',
    //         data : JSON.stringify({"action" : 'submit'}),
    //     }).done(function(data) {
    //         console.log(data);
    //     }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
    //         console.log(textStatus)
    //     })
    // });


    // tanaka password strength checker
    var $form = $("#pm-form");
    const message = "パスワードが一致していないもしくはパスワードが弱すぎます。"

    function formCancelSubmit(form, message){
        form.off("submit").on("submit", function(e){
        alert(message);
        e.preventDefault();
        });
    }
    //formCancelSubmit($form, message);
    $("#pm-input").pwdMeasure({
        minScore: 50,
        minLength: 8,
        labels: [
            {score:10,         label:"パスワードが弱すぎます",       className:"very-weak"},   //0~10%
            {score:30,         label:"パスワードが弱すぎます",       className:"weak"},        //11~30%
            {score:49,         label:"パスワードが弱すぎます",       className:"average"},     //31~50%
            {score:70,         label:"OK",        className:"strong"},      //51~70%
            {score:100,        label:"OK",        className:"very-strong"}, //71~100%
            {score:"notMatch", label:"不一致",     className:"not-match"},   //not match
            {score:"empty",    label:"未入力",     className:"empty"}        //empty
        ],
        indicator: "#pm-indicator",
        onValid: function(percentage, label, className){
            $form.off("submit");
        },
        onInvalid: function(percentage, label, className){
            formCancelSubmit($form, message);
        }
    });
});

// tanaka