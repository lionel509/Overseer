import os
from continuous_learning import ContinuousLearningManager

def test_log_and_retrieve():
    db_path = "test_user_interactions_encrypted.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ['OVERSEER_DB_KEY'] = 'testkey123'  # For test only
    mgr = ContinuousLearningManager(db_path=db_path)
    mgr.log_interaction("test input", "test response", {"foo": "bar"}, success=True, feedback=1)
    data = mgr.get_training_data(min_feedback=1)
    assert data[0]['input'] == "test input"
    assert data[0]['output'] == "test response"
    assert data[0]['context']['foo'] == "bar"
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_log_and_retrieve()
    print("Encrypted user interactions DB test passed.") 