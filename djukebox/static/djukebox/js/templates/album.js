<div class="span2 thumbnail" style="height: 25%">
<!-- album art to go here -->
    <h5>{{title}}</h5><br />
    <p>{{artist.name}} <!-- other album details --></p>
</div>
<div class="span10">
  {{#each tracks }}
  <div id="{{this.id}}" class="thumbnail track_item" mp3="{{this.mp3_stream_url}}" ogg="{{this.ogg_stream_url}}">
    {{this.title}}
  </div>
  {{/each}}
</div>
