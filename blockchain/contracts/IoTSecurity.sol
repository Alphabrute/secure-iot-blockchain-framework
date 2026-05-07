// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract IoTSecurity {

    struct Record {
        string deviceId;
        string dataHash;
        string status;
        uint256 timestamp;
    }

    Record[] public records;

    function storeRecord(
        string memory _deviceId,
        string memory _dataHash,
        string memory _status
    ) public {
        records.push(Record(
            _deviceId,
            _dataHash,
            _status,
            block.timestamp
        ));
    }

    function getCount() public view returns (uint256) {
        return records.length;
    }
}
