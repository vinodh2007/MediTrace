
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MedicineTracker {

    struct Medicine {
        string medicineId;
        string medicineHash;
        address registeredBy;
        uint256 timestamp;
        bool exists;
    }

    mapping(string => Medicine) private medicines;

    event MedicineRegistered(
        string medicineId,
        string medicineHash,
        address registeredBy,
        uint256 timestamp
    );

    // Register a medicine hash on the blockchain
    function registerMedicine(
        string memory _medicineId,
        string memory _medicineHash
    ) public {

        require(bytes(_medicineId).length > 0, "Medicine ID required");
        require(bytes(_medicineHash).length == 64, "Invalid SHA-256 hash");
        require(!medicines[_medicineId].exists, "Medicine already registered");

        medicines[_medicineId] = Medicine({
            medicineId: _medicineId,
            medicineHash: _medicineHash,
            registeredBy: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });

        emit MedicineRegistered(
            _medicineId,
            _medicineHash,
            msg.sender,
            block.timestamp
        );
    }

    // Verify a medicine hash
    function verifyMedicine(
        string memory _medicineId,
        string memory _medicineHash
    ) public view returns (bool) {

        Medicine memory medicine = medicines[_medicineId];

        return (
            medicine.exists &&
            keccak256(bytes(medicine.medicineHash)) ==
            keccak256(bytes(_medicineHash))
        );
    }

    // Get stored medicine information
    function getMedicine(
        string memory _medicineId
    ) public view returns (
        string memory,
        string memory,
        address,
        uint256,
        bool
    ) {

        Medicine memory medicine = medicines[_medicineId];

        return (
            medicine.medicineId,
            medicine.medicineHash,
            medicine.registeredBy,
            medicine.timestamp,
            medicine.exists
        );
    }
}
