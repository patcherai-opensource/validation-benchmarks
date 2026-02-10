<?php
class data_field_text {
    public $type = 'text';
    public $name = 'Text Input';
    public $description = 'A simple text input field';
    
    public function render() {
        return '<input type="text" class="form-control" />';
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
