<div class="container">
{{#each artists}}
  <div class="thumbnail">
    <span><a href="#artist/{{this.pk}}">{{this.fields.name}}</a></span>
  </div>
{{/each}}
</div>
