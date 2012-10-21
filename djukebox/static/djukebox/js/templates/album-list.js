{{#each albums}}
<div class="thumbnail">
  <span><a href="#album/{{this.id}}/">{{this.title}}</a></span><br />
  <span><a href="#artist/{{this.artist.id}}/">{{this.artist.name}}</a></span>
</div>
{{/each}}
