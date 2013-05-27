<fieldset>
    <legend>
      <h2>{{artist.name}}</h2>
    </legend>
    {{#each albums}}
    <div class="row">
      <div class="span2 well">
        <a href="#album/{{this.id}}">{{this.title}}</a>
      </div>
      <div class="span7">
        <table name="album_table" id="album_{{this.id}}" class="table table-bordered">
          {{#each this.tracks}}
          <tr data-delete>
            <td id="{{this.id}}" class="track_item" data-track-id="{{this.id}}" data-mp3="{{this.mp3_stream_url}}" data-ogg="{{this.ogg_stream_url}}" data-url="{{ this.resource_uri }}">
              <span>{{this.title}}</span>
              <div class="dropdown pull-right"><i role="button" class="icon-cog dropdown-toggle" data-toggle="dropdown"></i>{{> trackDropdown}}
              </div>
            </td>
          </tr>
          {{/each}}
        </table>
      </div>
    </div>
    {{/each}}
</fieldset>
