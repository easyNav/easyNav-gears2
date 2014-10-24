
var map = []

console.log('------------------------------------');
function GridClass () {
    this.$grid = $('.grid');
    this.grid = [[]]; 

    this.pos_x = 0;
    this.pos_y = 0;
    
    this.selectSquare = function (x, y) {
        // console.log("Incrementing square's selected value");
        // console.log("The object at x,y = " + JSON.stringify(this.grid[x][y]));
        // console.log("Full grid before:\n" + JSON.stringify(this.grid));
        this.grid[x][y].selected += 1;
        //console.log("Full grid after:\n" + JSON.stringify(this.grid));
        //this.drawGrid();
        //console.log("Why did entire row get incremented?");
    }

    this.writeSquare = function (x, y, text) {
        this.grid[x][y].selected += 1;
        this.grid[x][y].text = text;
        //this.drawGrid();
    }

    this.clearSquare = function (x, y) {
        this.grid[x][y].selected = 0;
        this.grid[x][y].text = "";
        //this.drawGrid();
    }
    
    this.drawGrid = function () {
        console.log("REDRAW");
        var h = "", rowClass = "";
        var xLen = this.grid.length;
        var yLen = this.grid[0].length;
        for (var y = yLen-1; y >= 0; y--) {
            for (var x = 0; x < xLen; x++) {
                var g = this.grid[x][y];

                if(g.text.length > 0){

                    if(g.text == "person"){
                        h += '<div class="' + rowClass 
                            + ' alt' + g.selected
                            + '"'
                            + ' data-x="' + x + '"'
                            + ' data-y="' + y + '"'
                            + '>'
                            + '<img src="arrow.png" id="img" alt="Smiley face" height="12" width="12">'
                            + " " 
                            ;
                        h += '</div>';  
                    }else{
                        h += '<div class="' + rowClass 
                            + ' alt' + g.selected
                            + '"'
                            + ' data-x="' + x + '"'
                            + ' data-y="' + y + '"'
                            + '>'
                            + " " + g.text
                            ;
                        h += '</div>';                        
                    }
    
                }else{
                    h += '<div class="' + rowClass 
                        + ' alt' + g.selected
                        + '"'
                        + ' data-x="' + x + '"'
                        + ' data-y="' + y + '"'
                        + '>'
                        + x + "," + y
                        + " " + g.text
                        ;
                    h += '</div>';               
                }

            }
            rowClass = "newRow";
            h += '<br />';
        }
        this.$grid.html(h);

    }

    this.setPos = function (x,y,angle) {


        //Check if map based
        key = this.pos_x.toString()+"-"+this.pos_y.toString();
        name = map[key];
        if(name.length !== undefined){

            if(typeof name === 'undefined'){
                this.clearSquare(this.pos_x,this.pos_y);
                grid.writeSquare(this.pos_x,this.pos_y, this.pos_x.toString()+","+this.pos_y.toString());
            }else{
                this.clearSquare(this.pos_x,this.pos_y);
                grid.writeSquare(this.pos_x,this.pos_y, name);
            }

            
        }else{
            this.clearSquare(this.pos_x,this.pos_y);
        }


        this.writeSquare(x,y,"person");
        this.writeSquare(x,y,"person");
        this.drawGrid();
        $("#img").rotate(angle);

        this.pos_x = x;
        this.pos_y = y;
    }
    
    this.createGrid = function () {
        var baseSize = 30;
        this.grid = [];
        for (var x = 0; x < 131; x++) {
            var blankYArray = [];
        
            for (var y = 0; y < 51; y++) {
                blankYArray.push({
                    "selected" : 0,
                    "text" : "",
                    "angle" : 0
                });
            }
        
            this.grid.push(blankYArray);
        }
    }

    // Construction
    this.createGrid();
    this.drawGrid();
    console.log("Initial Grid:\n" + JSON.stringify(this.grid));
}

function toDegrees (angle) {
  return angle * (180 / Math.PI);
}


$( document ).ready(function() {

    $('img').each(function() {
    var deg = $(this).data('rotate') || 0;
    var rotate = 'rotate(' + $(this).data('rotate') + 'deg)';
    $(this).css({ 
        '-webkit-transform': rotate,
        '-moz-transform': rotate,
        '-o-transform': rotate,
        '-ms-transform': rotate,
        'transform': rotate 
    });
    });

    console.log( "ready!" );
    grid = new GridClass();


    //Call Map
    $.ajax({
        url: 'http://192.249.57.162:1337/map',
        dataType: 'json',
        success: function(json){
            console.log(json);

            nodes = json["nodes"];
            edges = json["edges"];

            nodes.forEach(function(entry) {
                pos = entry["position"];
                name = entry["data"]["name"];
                console.log(pos);
                console.log(name);

                if(name=="person" || name=="path"){
                    return true;
                }

                xpos = Math.round(parseFloat(pos.x)/100);
                ypos = Math.round(parseFloat(pos.y)/100);

                console.log(pos);
                console.log(xpos);
                console.log(ypos);

                grid.selectSquare(xpos, ypos);
                grid.writeSquare(xpos, ypos, name);

                map[xpos.toString()+"-"+ypos.toString()] = name;


            });

            grid.drawGrid();

        }
    });

        // def post_heartbeat_location(self, x, y, z, ang):

        // payload = { "x": x, "y": y, "z": z, "orientation": ang/180.*np.pi }
        // if self.local_mode == 1:
        //     r = requests.post(self.local + "heartbeat/location", data=payload)
        // r = requests.post(self.remote + "heartbeat/location", data=payload)
        // return r.json()

    grid.$grid.on("click", "div", function(e){
        var $thisSquare = $(this);
        console.log("Clicked a square");
        console.log($thisSquare);
        var x = $thisSquare.data("x");
        var y = $thisSquare.data("y");

        $.post( "http://192.249.57.162:1337/heartbeat/semaphore", { x: x*100, y: y*100, val: 1 })
          .done(function( data ) {
            console.log(data);
            alert( data );
        });

        console.log("CLICK");
        console.log(x);
        console.log(y);

    });


    //Timer call
    //var myVar=setInterval(function () {myTimer()}, 3000);
    function myTimer() {


        $.ajax({
        url: 'http://192.249.57.162:1337/heartbeat',
        dataType: 'json',
        success: function(json){
            loc = json["location"];
            angle = loc["orientation"];
            loc = loc["loc"];
            loc = JSON.parse(loc);
            x = Math.round(parseFloat(loc.x)/100);
            y = Math.round(parseFloat(loc.y)/100);
            angle = toDegrees(angle);

            console.log(x);
            console.log(y);
            console.log(angle);

            grid.setPos(x,y,angle);
        }});

        //x++;
        console.log("A");
    }

});



