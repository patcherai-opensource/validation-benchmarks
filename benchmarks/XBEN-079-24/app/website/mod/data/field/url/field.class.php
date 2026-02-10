<?php
class data_field_url {
    public $type = 'url';
    public $name = 'URL Input';
    public $description = 'A URL/link input field';
    
    public function render() {
        return '<input type="url" class="form-control" placeholder="https://" />';
    }
    
    public function get_info() {
        return array(
            'type' => $this->type,
            'name' => $this->name,
            'description' => $this->description
        );
    }
}
?>
