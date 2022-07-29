var date=new Date();
        var year=date.getFullYear();
        var month=String(date.getMonth()+1).padStart(2,'0');
        var today_date=String(date.getDate()).padStart(2,'0');
        var datePattern=year + '-' + month + '-' + today_date;
        document.getElementById("cal").value=datePattern;