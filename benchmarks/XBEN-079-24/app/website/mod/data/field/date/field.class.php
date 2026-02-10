<?php
class data_field_date {
    public $type = 'date';
    public $name = 'Date Input';
    public $description = 'A date picker field';
    
    public function render() {
        return '<input type="date" class="form-control" />';
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
