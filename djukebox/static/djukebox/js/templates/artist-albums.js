<fieldset>
    <legend>
    <h2>{{artist.name}}</h2>
    </legend>
    {{#each albums}}
    <div class="row">
    <div class="span2 well">
        {{this.title}}
    </div>
    <div class="span7">
    <table name="album_table" id="album_{{this.id}}" class="table table-bordered">
    {{#each this.tracks}}
    <tr>
     <td id="{{this.id}}" class="track_item" mp3="{{this.mp3_stream_url}}" ogg="{{this.ogg_stream_url}}">
        <span>{{this.title}}</span>
      </td>
    </tr>
    {{/each}}
    </table>
    </div>
   {{/each}}
</div>
</fieldset>
